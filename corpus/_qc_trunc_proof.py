"""PROVE the truncated-axis test passes for the WRONG REASON.

The test asserts only '"FAIL" in sev'. But run_qc(p) without source_script always
fails provenance.generator. So the test cannot distinguish:
   (a) the gate detected truncation, or
   (b) the gate failed it for a missing generator script.
"""
import pathlib, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, r"E:\2026-AI4S\figpipe")
import figpipe.qc as qc

TMP = pathlib.Path(r"E:\2026-AI4S\figpipe\_qc_negative")
p = TMP/"truncated.pdf"
print("=" * 100)
print("THE TRUNCATED-AXIS NEGATIVE TEST: does it pass for the right reason?")
print("=" * 100)
print("  file:", p, "exists:", p.exists())
rep = qc.run_qc(p)          # exactly as the test calls it
checks = getattr(rep, "checks", [])
fails = [(getattr(c,"id","?"), getattr(c,"severity","?"), str(getattr(c,"detail",""))[:80])
         for c in checks if getattr(c,"severity","")=="FAIL"]
print()
print("  run_qc(p)  [as the test calls it] -> %d FAIL(s):" % len(fails))
for i, d, s in fails:
    print("     FAIL %-24s %s" % (i, s))
print()
print("  Is ANY of them a truncation check?  %s"
      % any("trunc" in i.lower() or "honest" in i.lower() or "axis" in i.lower() for i,_,_ in fails))
print()
print("  => the test asserts only '\"FAIL\" in sev', which the missing-generator")
print("     failure satisfies on its own. The test PASSES whether or not")
print("     truncation is detected.")

# Now with a generator supplied, does it STILL catch truncation?
gen = TMP/"truncated_gen.py"
gen.write_text(
 "import matplotlib\nmatplotlib.use('Agg')\n"
 "import matplotlib.pyplot as plt, numpy as np\n"
 "matplotlib.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'font.size':6})\n"
 "fig=plt.figure(figsize=(89/25.4,60/25.4)); ax=fig.add_subplot(111)\n"
 "x=np.arange(1,21); y=100+np.arange(20)\n"
 "ax.plot(x,y,color='#D55E00',lw=1.0)\n"
 "ax.set_ylim(y.min()-1,y.max()+1)\n"
 "ax.set_xlabel('position (n)'); ax.set_ylabel('count (unitless)')\n"
 "fig.savefig(r'%s', bbox_inches=None)\n" % str(TMP/"truncated_withgen.pdf"), encoding="utf-8")
import subprocess
subprocess.run([sys.executable, str(gen)], check=True, capture_output=True)

print()
print("=" * 100)
print("SAME FIGURE, WITH PROVENANCE SUPPLIED (the confound removed)")
print("=" * 100)
rep2 = qc.run_qc(TMP/"truncated_withgen.pdf", source_script=gen)
ok = rep2.ok() if callable(rep2.ok) else rep2.ok
checks2 = getattr(rep2, "checks", [])
fails2 = [(getattr(c,"id","?"), str(getattr(c,"detail",""))[:90])
          for c in checks2 if getattr(c,"severity","")=="FAIL"]
warns2 = [(getattr(c,"id","?"), str(getattr(c,"detail",""))[:90])
          for c in checks2 if getattr(c,"severity","")=="WARN"]
print("  ok=%s  FAIL=%d  WARN=%d" % (ok, len(fails2), len(warns2)))
for i,d in fails2: print("     FAIL %-24s %s" % (i,d))
for i,d in warns2: print("     warn %-24s %s" % (i,d))
print()
print("  *** A truncated y-axis with a generator script PRESENT: ok=%s ***" % ok)
