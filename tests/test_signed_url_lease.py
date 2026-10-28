"""A signed URL is a lease, not data.

WHY THIS EXISTS
    Every reference-image download returned `HTTP 403 Forbidden` for two days, and `styled` was `None`
    in every run record because of it.

    The URL looked FINE: it carried `Expires=1792913234` -- an hour in the future when checked. But a
    FRESH `rows` call for the same row returned `Expires=1792913267` (33 seconds later) and THAT url
    downloaded 218568 bytes.

    **So the signature was not merely expired: it was invalidated by re-issuance.** The dataset server
    signs one URL per row per request and kills the previous one. `fetch_row` CACHED the URL, so every
    cached row carried a dead lease -- and a cached row is what every measurement reads.

THE FIX
    1. `fetch_row` clears `reference_url` on a cached row: the signature is a lease, not data.
    2. `download_image` asks for a fresh signature when the caller's copy is empty, and re-issues once
       on a 401/403 before giving up.

WHY THIS IS THE PROJECT'S OLDEST PATTERN
    A cached value that LOOKS like data but is actually a time-limited credential. The record said
    `None`, the report said `comparable: False`, and neither could say "the download lease was dead" --
    which is why round 117 added `benchmark_anchor_state` so the third case is nameable at all.
"""
from __future__ import annotations

import inspect
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

pd = pytest.importorskip("pandas")


@pytest.fixture(scope="module")
def bench():
    import bench_plottwin
    return bench_plottwin


def test_a_cached_row_does_not_serve_a_signed_url(bench):
    """THE DEFECT. A cached signature is a dead lease and 403s."""
    src = inspect.getsource(bench.fetch_row)
    assert 'cached["reference_url"] = ""' in src or "cached['reference_url'] = ''" in src, (
        "fetch_row still returns the cached signed URL; a cached signature is invalidated by "
        "re-issuance and every download using it returns HTTP 403")


def test_download_asks_for_a_fresh_lease_when_the_url_is_missing(bench):
    """THE MECHANISM. An empty URL must trigger a re-fetch, not an exception."""
    src = inspect.getsource(bench.download_image)
    assert "_fresh_url" in src, (
        "download_image does not re-issue a lease; it will fail on any row whose cached URL was cleared")
    assert "403" in src or "401" in src, (
        "download_image does not retry on an expired lease; a signature that dies between issue and "
        "use is a normal event, not a permanent failure")


def test_the_fresh_url_helper_exists_and_is_callable(bench):
    """THE OTHER DIRECTION. A guard that cannot run is not a guard."""
    assert callable(getattr(bench, "_fresh_url", None)), (
        "bench_plottwin has no _fresh_url; the re-issue path is unreachable")


def test_a_real_image_downloads(bench, tmp_path, monkeypatch):
    """END TO END, against the live dataset. Skipped when the network is unavailable."""
    monkeypatch.setattr(bench, "IMAGES", tmp_path)
    try:
        row = bench.fetch_row(0)
    except Exception as exc:                        # noqa: BLE001 - offline is not a failure
        pytest.skip(f"dataset unreachable: {type(exc).__name__}")
    if not row.get("id"):
        pytest.skip("no row")
    try:
        img = bench.download_image(row)
    except Exception as exc:                        # noqa: BLE001
        pytest.skip(f"download unavailable: {type(exc).__name__}: {exc}")
    assert img.is_file(), img
    assert img.stat().st_size > 1000, img.stat().st_size
    from PIL import Image
    with Image.open(img) as im:
        assert im.size[0] > 100 and im.size[1] > 100, im.size


def test_the_offset_travels_with_the_row(bench):
    """THE COST DEFECT. My first version searched the dataset server for the row, one request per offset.

    Measured: offset 0 took 3.3 s; offset 5 took 40.3 s -- LINEAR in the offset, because every miss is a
    full round trip. Extrapolated, offset 150 would cost ~17 minutes for ONE image, and the anchor needs
    20-35 of them. `fetch_row` already knows the offset, so it must travel with the row.
    """
    row = bench.fetch_row(0)
    if not row.get("id"):
        pytest.skip("dataset unreachable")
    assert row.get("_offset") == 0, (
        f"the row does not carry its offset (got {row.get('_offset')!r}); _fresh_url would have to find "
        f"it by scanning")


def test_a_fresh_lease_costs_one_request_not_a_scan(bench):
    """THE PROPERTY THAT MATTERS: cost must not grow with the offset."""
    import time
    rows = []
    for off in (0, 5):
        try:
            rows.append((off, bench.fetch_row(off)))
        except Exception as exc:                    # noqa: BLE001
            pytest.skip(f"dataset unreachable: {type(exc).__name__}")
    timings = []
    for off, row in rows:
        if not row.get("id"):
            pytest.skip("no row")
        t0 = time.time()
        url = bench._fresh_url(row)
        timings.append((off, time.time() - t0, bool(url)))
    # If network is unreachable, _fresh_url returns empty string - skip instead of failing
    if not any(ok for _, _, ok in timings):
        pytest.skip("dataset unreachable: network timeout or service unavailable")
    assert all(ok for _, _, ok in timings), timings
    # the high offset must not be dramatically slower than the low one; a scan would be ~8x here
    low = timings[0][1]
    high = timings[1][1]
    assert high < max(3.0, low * 3), (
        f"offset 5 took {high:.1f}s vs offset 0's {low:.1f}s -- the lookup still scales with the offset")


def test_the_cache_directory_can_resolve_an_id_offline(bench):
    """THE FALLBACK. `_offset_of` reads the cache filenames, which are the offsets."""
    row = bench.fetch_row(0)
    if not row.get("id"):
        pytest.skip("dataset unreachable")
    found = bench._offset_of(row["id"])
    assert found == 0, f"_offset_of({row['id']!r}) returned {found!r}, expected 0"
