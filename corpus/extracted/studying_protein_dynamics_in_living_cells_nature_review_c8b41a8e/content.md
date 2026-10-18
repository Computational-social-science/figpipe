<!-- source: !!!!!Studying protein dynamics in living cells(Nature Review).pdf -->
<!-- source_pdf: D:\个人简历及资质材料\博士期间资料\学位论文研究资料\FRAP\!!!!!Studying protein dynamics in living cells(Nature Review).pdf -->
<!-- pages: 13 ; extracted_by: docling 2.140.0 -->

## STUDYING PROTEIN DYNAMICS IN LIVING CELLS

## Jennifer Lippincott-Schwartz, Erik Snapp and Anne Kenworthy

Since the advent of the green fluorescent protein, the subcellular localization, mobility, transport routes and binding interactions of proteins can be studied in living cells. Live cell imaging, in combination with photobleaching, energy transfer or fluorescence correlation spectroscopy are providing unprecedented insights into the movement of proteins and their interactions with cellular components. Remarkably, these powerful techniques are accessible to non-specialists using commercially available microscope systems.

With the genome sequences of many organisms now complete, research is turning to the study of protein function. Proteins are essential for most biological processes, but understanding their function is often difficult because proteins inside cells are not merely objects with chemically reactive surfaces. They localize to specific environments (that is,membranes, cytosol, organelle lumen or nucleoplasm), undergo diffusive or directed movement, and often have mechanical parts, the actions of which are coupled to chemical events. The fine tuning of geography,movement and chemistry gives proteins their extraordinary capability to regulate virtually all dynamic processes in living cells.

The discovery and development of GREEN FLUORESCENT PROTEIN (GFP) from the jellyfish Aequorea victoria, and more recently RED FLUORESCENT PROTEIN (DsRed) from the sea anemone Discosoma striata 1 , have revolutionized our ability to study protein localization, dynamics and interactions in living cells 2 . In so doing, these fluorescent proteins have allowed protein function to be investigated within the complex environment of the cell.Virtually any protein can be tagged with GFP, a β-barrel-shaped protein that contains an amino-acid triplet (Ser-Tyr-Gly) that undergoes a chemical rearrangement to form a fluorophore 3 . The resulting chimaera often retains parent-protein targeting and function when expressed in cells 2 , and therefore can be used as a fluorescent reporter to study protein dynamics.Advances in GFP biology,most notably the molecular engineering of the GFP-coding

GREEN FLUORESCENT PROTEIN Fluorescent protein cloned from the jellyfish Aequoria victoria. The most frequently used mutant, EGFP, is excited at 488 nm and has an emission maximum at 510 nm.

RED FLUORESCENT PROTEIN Fluorescent protein cloned from the sea anemone Discosoma striatawith an excitation maximum of 558 nm and emission maximum at 583 nm.

Cell Biology and Metabolism Branch, 18 Library Drive, NICHD,NIH Bethesda, Maryland 20892-5430 USA. Correspondence to J.L-S. e-mail: jlippin@helix.nih.gov sequence, have resulted in optimized expression of GFP in different cell types, as well as the generation of GFP variants with more favourable spectral properties, including increased brightness, relative resistance to the effects of pH variation on fluorescence, and photostability. BOX 1 summarizes properties of GFP and DsRed protein that are relevant for live cell imaging studies.

Paralleling the developments in GFP biology have been advances in fluorescence imaging methods and microscope systems that make it easy to visualize the localization of GFP fusion proteins, to quantitate their abundance and to probe their mobility and interactions. Imaging methods such as fluorescence recovery after photobleaching (FRAP), fluorescence resonance energy transfer (FRET) and fluorescence correlation spectroscopy (FCS) have been modified so that they can be done on user-friendly, commercially available laser scanning microscopes, replacing the need for custombuilt microscopes.Cost-effective computing resources have become available to handle large amounts of data, and powerful software packages are easily obtainable for analysing digital information. The combined advances in GFP biology, imaging methods and technical equipment are providing a tremendous stimulus for investigating the kinetic properties of proteins in living cells. In this review,we discuss some of these advances, focusing on the fluorescent imaging techniques that are being used to analyse protein movement and interactions in living cells.

<!-- image -->

## Box 1 | Fluorescent and chemical properties of GFP and DsRed

Green fluorescent protein (GFP)

- Fluorophore forms by chemical rearrangement of amino-acid triplet 3,7 .
- Various spectral variants available that can be used for fluorescence resonance energy transfer (FRET) and dual-colour imaging 2 .
- High fluorescence yield 2 .
- Resistant to photobleaching at low illumination 96 .
- Readily and irreversibly photobleached at high illumination 2 .
- Can partially reversibly photobleach over very short (millisecond) timescales 4 .
- Fluorescence is relatively insensitive to environment 2 .
- Optical shifting/blinking observed in single molecules 84,85 .
- Photoconverts under anaerobic conditions 82 .
- Complex photophysical states 7 .

Red fluorescent protein (DsRed)

- Red-shifted fluorescence compared with GFP 1 .
- Predicted to be good FRET acceptor for EGFP or EYFP 47 .
- Forms tetramers 97 .
- Difficult to photobleach 97 .
- Can take several days to convert from green to red fluorescence 97 .

Assessing the kinetic properties of a protein Proteins inside cells localize to two fundamentally different environments: they are either embedded in, or peripherally associated with,membranes; or they are in an aqueous phase, such as the cytoplasm, nucleoplasm or organelle lumen.Within these environments, a protein can freely diffuse, be immobilized to a scaffold, or be actively transported. These dynamic properties have crucial roles in determining what function a protein serves within the cell. GFP fusion proteins are ideal for studying these properties of proteins.Not only does the GFP fluorophore have a high fluorescence yield, which makes it bright, but also it is resistant at low illumination to photobleaching 4 - the photo-induced alteration of a fluorophore that extinguishes its fluorescence. These characteristics of the GFP fluorophore allow GFP chimaeras expressed within cells to be imaged with low light intensities over many hours, allowing a protein's steady-state distribution and life history to be studied 5 . Because with high illumination levels the GFP fluorophore can be photobleached, GFP chimaeras can also be used in photobleaching experiments to study movement of nonbleached GFP chimaeras into a photobleached area. Results from this type of experiment can provide important insights into a protein's diffusional properties and its movement between compartments within cells. Photobleaching can also be used to reduce fluorescence from background noise, so faint populations of fluorescent proteins can be visualized. In the next sections, we discuss how photobleaching, which traditionally has been viewed as something to avoid in fluorescence imaging, can be harnessed as a powerful technique for probing the mobility and kinetic properties of proteins in cells.

Fluorescence recovery after photobleaching. The mobility of a fluorescent protein can be assessed using a specific type of photobleaching technique called fluorescence recovery after photobleaching (FRAP). In this technique, fluorescent molecules in a small region of the cell are irreversibly photobleached using a high-powered laser beam and subsequent movement of surrounding nonbleached fluorescent molecules into the photobleached area is recorded at low laser power.GFP fusion proteins are ideal for use in FRAP studies because they can be bleached without detectable damage to the cell 5 .This is presumably because the compact barrel-like structure of GFP shields the external environment from the damaging effects that are caused by reactive intermediates generated by photobleaching 6,7 .

Two kinetic parameters of a protein can be discerned from quantitative studies that use FRAP: the mobile fraction,M f ,which is the fraction of fluorescent proteins that can diffuse into the bleached region during the time course of the experiment, and the diffusion constant,D, which is a measure of the rate of protein movement in the absence of flow or active transport 5,8,9 .Dreflects the mean squared displacement that a protein explores through a random walk over time and has units of area per time (usually cm 2 s -1 or µm 2 s -1 ).All proteins undergo this type of diffusive movement if they are not immobilized or experiencing active transport.Diffusion theory and the characteristics of a protein that underlie its Dare discussed in BOX 2.

## Box 2 | Diffusion theory

The diffusion constant for a particle in a free volume is described by the Stokes-Einstein formula (EQN 1):

<!-- image -->

<!-- formula-not-decoded -->

where D is the diffusion constant,T is the absolute temperature, η is the viscosity of the solution, k is the Boltzmann constant and R is the hydrodynamic radius of the particle. Because absolute temperature is usually constant within cells, the most important factors underlying Dare the size of a protein (or radius) and the viscosity of the medium within which it is diffusing. Membranes have a much higher viscosity than cytoplasm, so the lateral diffusion of a protein assembled within a membrane is considerably slower than that of a soluble protein, and this is reflected by a lower Dvalue.When the viscosity is constant, the D value of a protein is mainly determined by its radius or size. For a soluble spherical protein, an eightfold increase in size will lead to a twofold decrease in D. But this relationship does not hold for transmembrane proteins.Owing to the higher viscosity of membrane, the radius of the transmembrane segment dominates the Dvalue of a membrane protein,whereas the aqueous portion usually does not significantly contribute to the D value, at least in model membrane systems 15 . Even though viscosity and size are key factors underlying the diffusion rate of a protein, other factors also have a role in determining protein diffusion rates inside cells.These include protein-protein interactions or binding to a matrix that might slow or immobilize a protein, and collisions with other molecules,which hinder free diffusion. Such factors often prevent proteins from diffusing at their theoretical limit inside cells.

<!-- image -->

Figure 1 | Fluorescence recovery after photobleaching. a | Plot of fluorescence intensity in a region of interest versus time after photobleaching a fluorescent protein. The prebleach (F i ) is compared with the asymptote of the recovery (F∞ ) to calculate the mobile and immobile fractions. Information from the recovery curve (from F o to F∞ ) can be used to determine the diffusion constant of the fluorescent protein. b | Cells expressing VSVG-GFP were incubated at 40 °C to retain VSVG-GFP in the endoplasmic reticulum (ER) under control conditions (top panel) or in the presence of tunicamycin (bottom panel). Fluorescence recovery after photobleaching (FRAP) revealed that VSVG-GFP was highly mobile in ER membranes at 40 °C but was immobilized in the presence of tunicamycin. Adapted with permission from REF. 32 © (2000) Macmillan Magazines Ltd.

<!-- image -->

A typical FRAP curve,which provides information on D and M f is shown in FIG. 1a. The mobile fraction provides a measure of the extent to which the fluorescent protein can move within cells. It is determined by calculating the ratio of the final to the initial fluorescence intensity in the bleached region, corrected for the amount of fluorescence removed during photobleaching 4 .When the mobile fraction is less than 100%, some fluorescent molecules might be irreversibly bound to a fixed/anchored substrate.Alternatively, non-diffusional factors, such as diffusion barriers or discontinuites within the structure where a protein localizes,might be responsible for the reduced mobility 10,11-13 . The latter is common for proteins localized in internal compartments that are disconnected (for example, endosomes and lysosomes). The diffusion constant,D, is obtained by plotting the recovery of relative fluorescence intensity within the bleached region as a function of time, and fitting this recovery curve with various equations 8,12 (FIG. 1a). Equations that can been used to determine M f and Dfrom FRAP curves are shown in BOX 3.

The theoretical D for a protein is related to the size of a protein and its cellular environment (BOX 2). Deviations from this value can provide useful information about the environment of the protein (BOX 4). For example, a Dsignificantly lower than a predicted value (indicating slower diffusion) suggests that a fluorescent protein could be incorporated into an aggregate or a large complex, because D is inversely proportional to protein size.Alternatively, the environment of a protein could be notably more viscous than expected, or the protein could be interacting transiently with large or fixed molecules. By contrast, if D is significantly higher than predicted (indicating faster diffusion), the protein might be showing nondiffusive behaviour such as flow or directed movement by motor proteins, or the viscosity of the environment might be decreased. Similarly, changes in M f can reveal new information.A decrease in M f indicates that the protein could be binding to fixed molecules, forming immobile aggregates, or that the protein is confined to a compartment and cannot contribute to fluorescence recovery in a separate disconnected compartment 11,12,14 .When the M f increases, the protein has been released from either a restricted compartment or a fixed macromolecular complex. Given that there are many ways to interpret different Dand M f values shown by different proteins, combining FRAP

## Box 3 | Equations for M f and D

A simple equation for determining the mobile fraction M f from FRAP experiments is (EQN 1):

<!-- formula-not-decoded -->

where F∞ is the fluorescence in the bleached region after full recovery, F i is the fluorescence before bleaching and F 0 is the fluorescence just after the bleach.

D is obtained by plotting the recovery of relative fluorescence intensity within the bleach region as a function of time and fitting this recovery curve with various equations 8,13 (FIG. 1a).When a small spot or narrow strip is bleached, simple equations can be used for finding D, such as the equation by Axelrod and colleagues 8,13,16 (EQN 2):

<!-- formula-not-decoded -->

where ω is the radius of the focused laser beam, γ is a correction factor for the amount of bleaching, and τD is the diffusion time. This formula assumes unrestricted two-dimensional diffusion into a circular bleached area without recovery from above and below the focal plane, so it is valid only for diffusion in membranes. Formulas based on unrestricted diffusion in a free volume are used for characterizing protein diffusion in the cytoplasm.

<!-- image -->

## Box 4 | Interpreting D and M f

## Deviations from predicted D

## Increase in D

- Non-diffusive behaviour such as flow-directed movement by motor proteins.
- Decrease in environment viscosity.

## Decrease in D

- Formation of large aggregates or complexes (10-100-fold increase in molecular weight).
- Increase in environment viscosity.
- Transient interaction with large or fixed molecules.

## M f

100% mobile

- Protein is not restricted in ability to diffuse freely.

## Increase in M f

- Protein is released from restricted compartment.
- Protein is released from fixed macromolecular complex.

## Decrease in M f

- Protein binds to fixed molecules or forms aggregates that are restricted in movement.
- Protein is confined to compartment that cannot contribute to fluorescence recovery in a separate compartment.

data with biochemistry and cell biology is important for choosing the correct interpretation of the data.

Differences between theoretical and effective Dvalues for a protein can also arise from unusual cellular geometry.Equations of Dfor a protein in a membrane or a free volume usually assume that the spatial distribution of fluorescence in the cell is uniform 8 .However,GFP fusion proteins are not often distributed homogeneously within the cell, as occurs when complex three-dimensional structures (for example, the endoplasmic reticulum (ER) and Golgi) are labelled 14,15 . Relating the diffusive spread of fluorescence through such structures to an idealized planar membrane or volume has required the development of theoretical models and simulation programs that take topology into account 14,16-20 . More sophisticated equations and modelling are also required for analysing FRAP experiments in which there are several diffusing species or when recovery occurs by more than one process (for example, when diffusion and binding/release from a substrate occur) 13, 21-23 . Anomalous diffusion and flow-based processes can also contribute to recovery in FRAP experiments 13, 16, 23 ; the shape of the recovery curve is no longer characteristic of simple diffusion under these conditions.

Quantitative FRAP data. Results from quantitative FRAP experiments aimed at determining M f and D for GFP fusion proteins have provided important new insights into the kinetic properties of proteins in the aqueous (that is, cytoplasm, nucleoplasm and organelle lumen) and membrane environment of the cell. TABLE 1 provides a selected list of Dvalues for GFP and GFP chimaeras that illustrates the marked differences in D that these proteins have in different environments within the cell (see online supplementary material for a more extensive list).

Soluble GFP in the cytoplasm, the mitochondrial matrix and nucleus diffuse three to four times more

ULTRAVIOLET-LIGHT-INDUCED DNA DAMAGE Ultraviolet light promotes a covalent linkage of two adjacent pyrimidine bases (most often two thymines) in DNA.

NUCLEAR ENVELOPE Double membrane that surrounds the nucleus. The outer nuclear membrane is continuous with the endoplasmic reticulum. The outer nuclear membrane is connected to the inner nuclear membrane at nuclear pores.

NUCLEAR LAMINA Electron-dense layer lying on the nucleoplasmic side of the

inner membrane of a nucleus.

slowly than GFP in water, indicating that these environments are more viscous than water 4,17 .Despite this, inert molecules such as GFP can cross volumes the size of the nucleus (5-µm radius) rapidly 4 . The high mobility of small solute molecules in the cytoplasm and nucleus is likely to be important for coordinating the complex regulatory pathways that operate in these environments. Diffusion of GFP within the ER lumen revealed it to diffuse three- to sixfold slower than GFP in the cytoplasm, so the ER lumen seems more viscous than the cytoplasm 20 .The abundance of protein-folding machinery and branched carbohydrate side-chains on proteins in the ER lumen could explain why its viscosity is greater than that of the cytoplasm.The apparent mobility of several nucleoplasmic GFP fusion proteins (for example, GFP fused to high mobility group 17, SF2/ASFor fibrillarin) measured in FRAP experiments is surprisingly low (D= 0.24-0.53 µm 2 s -1 ) 21,24 .As these proteins have been shown to associate rapidly with larger steady-state structures in the nucleus (that is, splicing factor complexes and the nucleolus), one explanation for their low D is that recovery reflects two processes: diffusion and binding/release from an immobile substrate 21,24 . In a related study by Houtsmuller et al. 25 , a GFP-tagged DNA-repair nuclease was shown to diffuse at the rapid rate of 15 µm 2 s -1 under normal conditions, but to undergo temporary immobilization after ULTRAVIOLET LIGHT-INDUCED DNA DAMAGE.

FRAP studies of GFP-tagged membrane proteins are providing insight into how proteins are retained in different membrane-bounded compartments of the cell. Most ER-localized GFP fusion proteins are highly mobile in this compartment with little or no immobile fraction (FIG. 1b). The Dmeasured for these proteins ranges from 0.2-0.5 µm 2 s -1 (TABLE 1 and online supplementary material),which is near the theoretical limit for protein diffusion in a lipid bilayer 26 , so there seem to be few constraints to their diffusion.A Dvalue has been reported that is five to ten times lower than that for GFP-tagged TAP (transporter associated with antigen processing;molecule that participates in peptide loading of MHC class I molecules). TAP exists in the ER as a supramolecular complex, 10 6 kDa in size 27 , so its large size is likely to underlie its reduced D value. FRAP studies using GFP-tagged Golgi resident enzymes have shown that these proteins are also highly mobile in Golgi membranes with no constraints to their lateral diffusion 15,28 . Protein localization in ER and Golgi compartments thus relies on mechanisms other than immobilization. The rapid lateral mobility of ER and Golgi proteins is likely to be important for coupling the protein processing and transport reactions occurring within the membranes of these organelles.

The Dof many proteins embedded in the plasma membrane is considerably lower than that of proteins in the ER and the Golgi 11 . This suggests that there are constraints to protein diffusion at the cell surface, possibly due to interactions with the peripheral cytoskeleton or with the extracellular matrix 12,29,30 . Likewise, there is little or no diffusion of proteins enriched in the inner NUCLEAR ENVELOPE 13 , presumably because of tight binding interactions with the LAMINA and chromatin. Because

<!-- image -->

| Table 1 &#124; Diffusion rates of GFP and GFP chimaeras using FRAP                                                  | Table 1 &#124; Diffusion rates of GFP and GFP chimaeras using FRAP   |
|---------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Molecule                                                                                                            | D (µm 2 s -1 )                                                       |
| GFP in water 4 GFP in cytoplasm 4 GFP in the endoplasmic-reticulum (ER) lumen 20 GFP in the mitochondrial matrix 17 | 87 25 5-10 20-30                                                     |
| ER membrane                                                                                                         | ER membrane                                                          |
| VSVG tsO45-GFP (in ER+BFA 32 o C) 32 VSVG tsO45-GFP (in ER 40 o C) 32 Signal recognition particle β-subunit-GFP 32  | 0.49 0.45 0.26                                                       |
| Golgi apparatus membrane                                                                                            | Golgi apparatus membrane                                             |
| Galactosyltransferase-GFP (in Golgi) 15 Nucleoplasm                                                                 | 0.54                                                                 |
| GFP-fibrillarin 21                                                                                                  | GFP-fibrillarin 21                                                   |
| GFP-ERCC1/XPF 25 E-cadherin-GFP 31                                                                                  | 0.53 15                                                              |
| Plasma membrane                                                                                                     | Plasma membrane                                                      |
|                                                                                                                     | 0.03-0.04                                                            |

VSVG, vesicular stomatitis virus G protein; BFA, brefeldin A.

TUNICAMYCIN An antibiotic that inhibits the glycosylation of asparagine residues yielding carbohydratepoor glycoproteins.

many of the functions of proteins localized to the plasma membrane and nuclear envelope require tight binding interactions with other proteins, it is not surprising that some membrane proteins in these compartments are relatively immobile.

Changes in the mobility of GFP fusion proteins observed under different conditions can provide insight into how a protein changes its association with other proteins. For example, a GFP-tagged lamin-B receptor during mitosis changed from being immobilized in nuclear envelope membranes to being highly mobile in the ER,presumably as a result of its release from nucleoplasmic structures such as the lamina and chromatin 14 . During polarization, a GFP-E-cadherin protein in epithelial cells changed from being highly mobile on the plasma membrane to largely immobile after recruitment to sites of cell-cell contact 31 .Moreover,ATP depletion or TUNICAMYCIN treatment led an ER-localized viral glycoprotein that was highly mobile to become immobilized, indicating that it might have become crosslinked to ER chaperones 32 (FIG. 1b). FIGURE 2 and BOX 4 summarize the types of change in Dand the M f that can be observed and how to interpret them.

Figure 2 | Mechanisms that reduce the mobility of membrane proteins. a | An unrestricted membrane protein freely diffuses in the lipid bilayer of the membrane, as is seen with VSVG-GFP in the endoplasmic reticulum and galactosyltransferase-GFP in the Golgi complex 15,32 . b | Membrane proteins bound to an immobile matrix, such as the extracellular matrix or chromosomes, become immobilized. c | Large multimeric complexes of proteins, such as the TAP complex (10 6 kDa), diffuse at significantly reduced rates within the bilayer compared with monomeric proteins with small transmembrane radii. d | Corralling of a membrane protein by aggregated or matrixbound membrane proteins effectively reduces the mobility of the protein.

<!-- image -->

Fluorescence loss in photobleaching. In this photobleaching technique, loss of fluorescence rather than fluorescence recovery is monitored. Fluorescence in one area of the cell is repeatedly bleached while images of the entire cell are collected (FIG. 3). If fluorescent molecules from other regions of the cell can diffuse into the area being bleached, loss of fluorescence will occur from both places, indicating that the regions are connected and the protein can diffuse between them. Fluorescence loss in photobleaching (FLIP) experiments done in this way have helped clarify the extent of continuity of various intracelluar membrane systems 5,9,15 . For example, soluble and membrane-bound GFP fusion proteins localized in the ER showed complete loss of fluorescence upon repetitive bleaching of a small area in the ER 14,15,28,32-34 (FIG. 3) indicating that membranes and lumenal spaces of the ER are normally continuous throughout the cell. Golgi membranes in animal cells and plastids in plant cells, likewise,were shown to be largely continuous using FLIP, with resident proteins diffusing along tubules that extended between elements of these organelles 15,35 .When Golgi elements were fragmented during microtubule depolymerization, FLIP experiments showed pockets of fluorescence that remained unbleached, even between elements in close proximity 36 , indicating that in the absence of microtubules the lateral tubule connections between Golgi elements might no longer exist. FLIP experiments have also revealed the properties of ER and Golgi membranes during mitosis. Mitotic ER membranes were shown to remain as elaborate membrane networks, with little or no fragmentation or vesiculation 14 . Likewise, no evidence of a vesicle or fragment pool of Golgi proteins was observed in FLIP experiments in metaphase cells, consistent with a model in which these proteins have redistributed into the membranes of the ER during mitosis 28 . So, FLIP experiments can address whether a protein can diffuse uniformly across a compartment or whether there are regions of restricted mobility.

Other applications of FRAP. Not all protein movement within cells occurs by diffusion. For example, some proteins are transported between compartments within membrane-bounded vesicles,which track through the cytoplasm along cytoskeletal fibres. It is difficult to gain insight into the rate of this movement in cells by only observing GFP chimaeras at steady state. By selectively photobleaching the donor but not the acceptor compartment (or vice versa), however, vesicle transport of GFP-tagged cargo can be monitored by recording the rate of fluorescence recovery in the bleached compartment.This approach has been used to measure the rate at which Golgi markers cycle between the ER and the Golgi using membrane-bounded transport intermediates 28 . In such experiments,Golgi or ER pools of GFPtagged Golgi proteins were selectively photobleached and then recovery from the unbleached pool was moni- FCS, fluorescence correlation spectroscopy; FLIP, fluorescence loss in photobleaching, FRAP, fluorescence recovery after photobleaching; FRET, fluorescence resonance energy transfer.

<!-- image -->

| Table 2 &#124; Fluorescence-microscope-based methods for studying protein dynamics and interactions in living cells - Technique   | Table 2 &#124; Fluorescence-microscope-based methods for studying protein dynamics and interactions in living cells - Applications   | Table 2 &#124; Fluorescence-microscope-based methods for studying protein dynamics and interactions in living cells - Advantages                                                                                                                 | Table 2 &#124; Fluorescence-microscope-based methods for studying protein dynamics and interactions in living cells - Disadvantages                 | Table 2 &#124; Fluorescence-microscope-based methods for studying protein dynamics and interactions in living cells - References   |
|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| FRAP                                                                                                                              |                                                                                                                                      |                                                                                                                                                                                                                                                  |                                                                                                                                                     |                                                                                                                                    |
| Quantitative FRAP                                                                                                                 | Measurements of D and M f                                                                                                            | Can be done on many confocals Fast Methodology well established                                                                                                                                                                                  | Analysis depends on geometry of compartment Difficult to separate multiple components                                                               | 5                                                                                                                                  |
| FLIP                                                                                                                              | Assesses continuity of compartments                                                                                                  |                                                                                                                                                                                                                                                  | Non-quantitative                                                                                                                                    | 5,15                                                                                                                               |
| Selective photobleaching                                                                                                          | Exchange of proteins on/off membranes Traffic between compartments Dynamics of protein assemblies Enhancing dim objects              | Can alter steady-state distribution of fluorescently labelled proteins Quantitative Nondestructive and noninvasive Can bleach structures with complex shape Can bleach one of two colours in double-labelled cells Can link to kinetic modelling | Requires specialized confocal software and/or hardware for complex geometry bleaches                                                                | 28                                                                                                                                 |
| FRET Sensitized acceptor                                                                                                          | See Table 3                                                                                                                          | True readout of FRET Provides fast qualitative measurements                                                                                                                                                                                      | Requires extensive correction factors Sensitive to photobleaching                                                                                   | 98                                                                                                                                 |
| Acceptor photobleaching /Donor quenching                                                                                          |                                                                                                                                      | Straightforward and quantitative Done on a single sample                                                                                                                                                                                         | Destructive so single measurement only Slow                                                                                                         | 74,99                                                                                                                              |
| Donor photobleaching                                                                                                              |                                                                                                                                      | Minimal correction factors Quantitative Exploits photobleaching                                                                                                                                                                                  | Photobleaching is a complex process Need to compare two samples Destructive so single measurement only                                              | 100,101                                                                                                                            |
| Fluorescence lifetime imaging microscopy                                                                                          |                                                                                                                                      | Lifetimes can be accurately measured Independent of fluorescence intensity                                                                                                                                                                       | Requires specialized instrumentation                                                                                                                | 53,54                                                                                                                              |
| Anisotrophy (homotransfer)                                                                                                        |                                                                                                                                      | Fast, non-destructive Single sample                                                                                                                                                                                                              | Measures FRET between similar molecules                                                                                                             | 73                                                                                                                                 |
| FCS                                                                                                                               |                                                                                                                                      |                                                                                                                                                                                                                                                  |                                                                                                                                                     |                                                                                                                                    |
|                                                                                                                                   | Measurements of D Detects protein-protein interactions Also see Table 4                                                              | Measures absolute concentrations Single molecule sensitivity Very fast Readily separates many components Can measure using autocorrelation or cross-correlation analysis Can measure photophysical properties of fluorophores                    | Methodology in cells is still experimental Requires specialized instrumentation Requires low fluorophore concentrations Sensitive to photobleaching | 76-78                                                                                                                              |

tored. Because recovery occurred in the absence of new protein synthesis, the data indicate that the steady-state concentrations of fluorescent Golgi proteins in the Golgi and the ER arise by continuous protein cycling between these compartments rather than by stable protein retention in the compartments. Data obtained from this type of experiment can be used to model kinetically the cycling rates between compartments, which can provide rate constants and residency times for proteins in different compartments 28,36 .

The rate of exchange of cytosolic proteins on and off membranes has also been investigated using selective photobleaching methods. Photobleaching of peripheral coat proteins tagged with GFP, including ARF1, εCOP and SEC13, has been used to measure how rapidly these proteins cycle on and off membranes of the early secretory pathway 37-39 ,which is important in clarifying the role of coat proteins in membrane budding and fusion events. Likewise, various signalling molecules tagged with GFP have been shown in photobleaching experiments to

ARF1 Small GTPase that regulates the assembly of coats and vesicle budding.

εCOP One of seven subunits of the COPI coatomer complex. SEC13 Component of the COPII coat complex.

translocate from the cytosol to the plasma membrane in response to different stimuli 40 .The use of kinetic modelling approaches for analysing data from these types of experiment can be useful for determining rates of binding and release of a protein from a substrate.

Selective photobleaching techniques can also be used to determine whether protein assemblies in the cell, such as signalling complexes, ribosomes and the nucleolus, are stable structures that persist for long periods of time or are dynamic steady-state systems with proteins rapidly binding and being released. Recently, Phair and Misteli 21 have addressed this question for two protein assemblies found in the nucleus - the nucleolus and the splicing factor compartment.After localization of GFPtagged markers to each of these compartments (including GFP-SF2/ASF in the splicing-factor compartment and GFP-fibrillarin in the nucleoleus), they selectively photobleached each of these structures. Strikingly, both structures showed rapid recovery of fluorescence, indicating that GFP-SF2/ASF and GFP-fibrillarin were continuously and rapidly associating/dissociating from these structures. By combining these data with results using FLIP, these authors applied kinetic modelling to determine relative rate constants for protein association and dissociation from these compartments and the residence time of proteins in the compartments. These techniques will allow us to test whether other large protein assemblies within the cell (for example, PROTEASOMES and ribosomes) are also steady-state systems,the resident components of which are undergoing constant association and disassociation. For example, FRAP experiments showed that proteasomes can diffuse freely within the cytoplasm and nucleus, but not between them 41 .

<!-- image -->

Figure 3 | Fluorescence loss in photobleaching. Protein fluorescence in a small area of the cell (box) is bleached repetitively. Loss of fluorescence in areas outside the box indicates that the fluorescent protein diffuses between the bleached and unbleached areas. Repetitive photobleaching of an endoplasmic reticulum (ER) GFP-tagged membrane protein reveals the continuity of the ER in a COS-7 cell. Image times are indicated in the lower right corners. The postbleach image was obtained immediately after the first photobleach. The cell was repeatedly photobleached in the same box every 40 s. After 18 min, the entire ER fluorescence was depleted, indicating that all of the GFP-tagged protein was highly mobile and that the entire ER was continuous with the region in the bleach box. Adapted with permission from REF. 32 © (2000) Macmillan Magazines Ltd.

<!-- image -->

A different application of selective photobleaching is to enhance the imaging of dim structures in cells or in areas of the cell next to very bright objects. Examples of this application include photobleaching of background fluorescence to visualize fluorescently labelled secretory transport carriers en route to the plasma membrane, and the bleaching of Golgi fluorescence to visualize cargo delivery to this organelle 42-44 .

Measuring protein-protein interactions Defining the repertoire of interactions that a particular protein can undergo is crucial for understanding its function and regulation.Approaches such as biochemical co-immunoprecipitation experiments and yeast two-hybrid screens have yielded a wealth of information about the specific associations of various proteins. Using novel forms of fluorescence microscopy, these observations can now be complemented and extended in real time in living cells. Pairs of interacting proteins are too small to be resolved by conventional fluorescence microscopy.However,with the help of two other fluorescence-based techniques, fluorescence resonance energy transfer (FRET) and fluorescence correlation spectroscopy (FCS), it is now possible to generate maps of protein interactions using a fluorescence microscope. The first of these methods, FRET, detects the close proximity of interacting proteins.An emerging technique, FCS, detects either changes in the diffusion or the codiffusion of bound species.Below,we discuss how these techniques are markedly enhancing our ability to

## PROTEASOMES

Large multisubunit protease complex that selectively degrades intracellular proteins. Targeting to proteasomes most often occurs through attachment of multi-ubiquitin tags.

CYAN FLUORESCENT PROTEIN S65A, Y66W, S72A, N1461I, M153T,V163A mutant of green fluorescent protein with excitation peak of 434 nm and an emission maximum at 477 nm.

YELLOW FLUORESCENT PROTEIN S65G, V68L, S72A, T203Y mutant of green fluorescent protein with an excitation peak of 514 nm and an emission maximum at 527 nm.

resolve protein-protein interactions spatially and temporally in living cells.

FRET microscopy. A prerequisite for two proteins to interact in a cell is that they are present in the same intracellular compartment. Testing whether this is the case is traditionally accomplished by fluorescence colocalization studies. In such an experiment, the proteins of interest are labelled with fluorescent probes, each fluorophore having distinct excitation and emission spectra.Normally,when one fluorophore is excited, fluorescence is emitted only at wavelengths characteristic for that fluorophore, and vice versa (FIG. 4a).However, certain pairs of fluorophore such as CYAN FLUORESCENT PROTEIN (CFP) and YELLOW FLUORESCENT PROTEIN (YFP) can under-

<!-- image -->

Distance between donor and acceptor (Å)

Figure 4 | Principles of FRET. a | No FRET is detected between two fluorescently tagged soluble proteins (blue and red) that co-localize, but do not undergo specific protein-protein interactions. Here, excitation of the donor fluorophore (CFP) results in the emission of donor fluorescence. b | FRET occurs between two fluorescently tagged soluble proteins (blue and green) that bind one another. Here, when the donor fluorophore is excited, 'sensitized' acceptor fluorescence is observed. c | Dependence of energy transfer efficiency E on the distance r between the donor and acceptor for proteins in solution. Plots are shown for three values of R 0 , 30 Å (blue), 50 Å (red) and 70 Å (green). Note that E drops off to zero at separations of &gt; 100 Å (&gt;2R 0 ) for R 0 = 50 Å.

<!-- image -->

QUANTUM YIELD The probability of luminescence occurring in given conditions, expressed by the ratio of the number of photons (the quanta of light) emitted by the luminescing species to the number absorbed.

## FITC

Fluorescent dye with an excitation maximum of 492 nm and an emission maximum of 520 nm.

## RHODAMINE

Fluorescent dye with an excitation maximum at 550 nm and an emission maximum at 590 nm.

## CY3

Fluorescent cynanine dye with an excitation maximum at 550 nm and an emission maximum at 570 nm.

## CY5

Fluorescent cynanine dye with an excitation maximum at 650 nm and an emission maximum at 670 nm.

REPORTER CONSTRUCTS Artificial proteins engineered to act as intracellular sensors. Often consist of a pair of GFP mutants that act as a FRET pair linked by a peptide that undergoes conformational changes or is physically altered in response to the intracellular environment or enzyme activity.

## CY3.5

Fluorescent cynanine dye with an excitation maximum at 580 nm and an emission maximum at 590 nm.

<!-- image -->

Figure 5 | Examples of recent applications of FRET microscopy. a | Test for preassembly of oligomeric receptor complexes. FRET occurs when CFP- and YFP-tagged receptor monomers are assembled into a complex but is much less if the receptors are not oligomerized. Oligomerization occurring in response to ligand binding can also be detected using this technique. This kind of approach was used to show that Fas is preassembled in a trimer before binding of its ligand, FasL 68 . b | Detection of specific phosphorylation of a receptor tyrosine kinase. Here, FRET occurs when a CY3.5labelled anti-phosp-hotyrosine antibody binds to a GFPtagged receptor, bringing the fluorophores within FRET proximity. Example is adapted from REF. 52. c | FRET assay for detecting lipid raft domains. Putative raft-resident proteins are labelled with donor and acceptor fluorophores. FRET will systematically increase with increasing surface density provided that the proteins are randomly distributed. If the proteins are instead concentrated in raft domains, FRET will be independent of surface density. This type of approach was used to show that some 73 , but not all 74,75 , lipid raft proteins appear to be enriched in such domains at the cell surface.

go a process known as FRET (reviewed in REFS 45, 46). When CFP and YFP are in very close proximity to one another, excitation of CFP results in 'sensitized' fluorescence emission by YFP, due to a transfer of the energy absorbed by CFP to YFP (FIG. 4b). CFP fluorescence is concomitantly quenched (FIG. 4c).A FRET pair such as CFP and YFP is defined in terms of a 'donor' and 'acceptor', in which the emission spectrum of the donor (CFP) significantly overlaps with the excitation spectrum of the acceptor (YFP).

FRET microscopy complements fluorescence colocalization studies by providing a readout of the molecular proximity of the donor- and acceptor-labelled proteins. This is possible because FRET is strongly dependent on the distance between the donor and acceptor, falling off with the sixth power of the distance between the two.How much energy transfer is observed at a given separation distance also depends on the particular donor and acceptor pair.A Förster distance,R 0 , can be calculated for a given donor and acceptor pair; when the two fluorophores are separated by this distance (r = R 0 ), energy transfer occurs with an efficiency of 50%.For CFP and YFP, for example, R 0 is ~50 Å, so when the donor and acceptor are separated by more than 100 Å (r &gt; 2R 0 ), no FRET occurs. R 0 depends on the extent of spectral overlap between the donor and acceptor and the QUANTUM YIELDof the donor. It also depends on the relative orientation of the donor and acceptor; if this is unfavourable, no FRET will occur. FRET can be measured in various ways, including quenching of donor fluorescence, sensitized acceptor fluorescence, acceptor photobleaching, anisotropy, a decrease in the lifetime of the donor in the excited state, and a decrease in the rate of donor photobleaching. Importantly, all of these processes can be detected by fluorescence microscopy.

To detect protein-protein interactions using FRET microscopy, several FRET pairs and labelling schemes are available. Spectral variants of GFP and DsRed 1 provide useful FRET pairs 47-50 . It should be noted that a donor CFP and acceptor YFP fluorophore can never come closer than ~30 Å from one another as they are each buried ~15 Å within the protein. FRET microscopy is, of course, not limited to the use of GFP chimeric proteins.Many conventional fluorophores commonly used in fluorescence co-localization experiments, such as FITC and RHODAMINE, and CY3 and CY5 are excellent FRET pairs 45,51 . In fact, samples for FRET measurements can be prepared by immunofluorescence techniques, or using fluorescently tagged proteins. A limitation of intracellular FRET measurements using non-GFP fluorophores, however, is the requirement for microinjection or the use of fixed cells. FRET can also be measured between GFP-tagged protein and, for example, Cy3 or Cy5 (REFS 52-55).

Applications of FRET microscopy. FRET is perhaps best recognized by biologists for its use in a wide range of REPORTER CONSTRUCTS, including sensors of intracellular Ca 2+ , cyclic AMP, cGMP, protease activity and gene expression 56-66 . However, FRET microscopy and its variations have much broader applications, and have proved useful to address questions as diverse as the interactions of circadian clock proteins in bacteria 67 and the activation state of protein kinase Cα in archived tissue samples 54 (TABLE 3). One area where FRET microscopy has made especially important contributions during the past year is cell signalling. Binding of extracellular ligands to transmembrane receptors at the cell surface initiates several intracellular signalling pathways. Transduction of the signal that indicates that a ligand has bound often requires the formation of a complex between an oligomeric receptor and the ligand. For example, Fas, a cell surface receptor, transduces an apoptotic signal upon binding of its trimeric ligand, FasL. Until recently, Fas was thought to exist as a monomer that assembled into a trimer upon FasL binding. However, FRET studies using fusion proteins between Fas and CFP or YFP now show that Fas exists as a preassembled trimer on the cell surface 68 (FIG. 5a). This trimerization is mediated by a pre-ligand assembly domain in the extracellular region of the protein. This domain is a common feature of receptors in the tumour necrosis factor superfamily, and it also regulates the preassembly of receptor complexes of homologues of Fas, tumour necrosis factor receptor-1 and -2 (REF. 69). These FRET results indicate that, at least for the case of Fas and FasL, receptor assembly might have a predominant role in regulating signalling. Because of its fundamental implications for potential mechanisms of signal transduction, the relationship between receptor oligomerization and ligand binding is a question being actively pursued for many cell surface receptors (TABLE 3).

<!-- image -->

Figure 6 | Principles of fluorescence correlation spectroscopy. a | As a fluorescently tagged protein diffuses through the confocal volume, the attached fluorophore (here, GFP) emits photons. Individual proteins (left) diffuse faster and thus reside in the volume for less time than proteins that are bound in a complex (right). b | From measurements of the corresponding fluctuations in fluorescence intensity over time, an autocorrelation curve can be calculated. Each autocorrelation curve contains information about the average number of particles, N, diffusing through the volume (G 0 = 1/N), as well as the characteristic correlation time τD for this process. If several components are present, this analysis can also resolve the fraction of each (right). The correlation time τD is related to the diffusion constant D and the width of the confocal volume ω1 by D = ω1 2 /4τD . So, a shorter correlation time corresponds to a protein with faster diffusion (larger D).

<!-- image -->

How and where downstream events in signalling are activated and subsequently deactivated is another question readily addressed by FRET microscopy. In the case of the epidermal growth factor receptor (EGFR), the receptor is autophosphorylated on specific tyrosine residues upon ligand binding and receptor dimerization. The phosphotyrosines permit the sequential binding of a series of downstream adaptor and effector proteins. To study the time course, extent and subcellular distribution of the activated form of this receptor tyrosine kinase,Wouters and colleagues 52 measured FRET between a GFP-tagged version of the EGFR and a Cy3-labelled anti-phosphotyrosine antibody after EGF stimulation. Using this approach, specific phosphorylation of EGFR-GFP could be detected even using nonspecific anti-phosphotyrosine antibodies (FIG. 5b).At early times after EGF stimulation, significant FRET was detected between Cy3-phosphotyrosine antibody and the GFP-tagged receptor. The FRET

*Used GFP-tagged proteins. CR, complement receptor; EGFR, epidermal growth factor receptor; MHC, major histocompatibility complex; PKCα, protein kinase Cα; PKA, protein kinase A; SNARE, soluble NSF attachment protein receptor, where NSF stands for N-ethyl-maleimide-sensitive fusion protein; TNF, tumour necrosis factor.

| Table 3 &#124; Applications of FRET microscopy   | Table 3 &#124; Applications of FRET microscopy   |
|--------------------------------------------------|--------------------------------------------------|
| Application                                      | References                                       |
| Reporter constructs                              |                                                  |
| Ca 2+ sensors*                                   | 56-58                                            |
| Cyclic AMP sensors*                              | 59                                               |
| Protease substrates*                             | 61-65                                            |
| Gene expression                                  | 66                                               |
| Phosphorylation state sensor for PKA             | 102                                              |
| Cyclic GMP sensor                                | 60                                               |
| Supramolecular complex organization              |                                                  |
| Adherens junction                                | 103                                              |
| Centrosome                                       | 98                                               |
| SNARE complex*                                   | 104                                              |
| Peroxisomal proteins                             | 105                                              |
| CTL-target cell contact                          | 106                                              |
| Receptor oligomerization state                   |                                                  |
| EGFR                                             | 107,108                                          |
| β2 -adrenergic receptor*                         | 109                                              |
| Fas*                                             | 68                                               |
| TNFα receptors*                                  | 69                                               |
| Biotin/streptavidin                              | 110                                              |
| Protein phosphorylation state                    |                                                  |
| EGFR*                                            | 52                                               |
| PKCα*                                            | 54                                               |
| Membrane microdomain structure                   |                                                  |
| MHC class I clustering                           | 100                                              |
| Lipid raft organization                          | 73-75                                            |
| Other protein-protein interactions               |                                                  |
| Bax-Bcl-2*                                       | 111                                              |
| PKCα-β1 integrin*                                | 55                                               |
| PKA-anchoring protein*                           | 112                                              |
| Cholera toxin A-B subunits                       | 99                                               |
| FcyRIIIB-CR3                                     | 113                                              |
| Circadian clock proteins*                        | 67                                               |
| Transport receptors-nucleoporins*                | 114                                              |
| Transcription factors*                           | 115-118                                          |

<!-- image -->

AUTOCORRELATION FUNCTION Mathematical function that is used to extract statistical properties of time-dependent noise.Used to analyse timedependent fluctuations of fluorescence intensity in an FCS experiment to find similarities within the signal - for example, a correlation time reflecting diffusion of a fluorescent protein through a sample volume.

TWO-PHOTON MICROSCOPY A form of multiphoton microscopy.

## FLASH

A membrane-permeable fluorophore (fluorescein arsenical helix binder) that specifically, non-covalently, and reversibly binds a recombinant protein motif containing four cysteines at the i, i+1, i+4, and i+5 positions.

SINGLE-CHAIN ANTIBODIES Peptides derived from immunoglobulins (which usually consist of two heavy chains and two light chains). These peptides do not oligomerize and have specific affinity for an antigen.

TOTAL INTERNAL REFLECTION MICROSCOPY

Fluorescence microscopy technique with significant depth discrimination, that can selectively excite only those fluorescent molecules within 100 nm of the interface between a cell and a coverslip.

MULTIPHOTON MICROSCOPY Microscopy technique that uses the simultaneous absorbance of two or more photons of low energy (long wavelength) to excite fluorophores normally excited with single photons of shorter wavelengths. The technique reduces photodamage and permits imaging of much thicker samples.

IMAGE CORRELATION SPECTROSCOPY Technique that measures the density and degree of aggregation of fluorescent particles using autocorrelation analysis of images from laser scanning confocal microscopy. Can be used, for example, to measure quantitatively the state of aggregation of receptors on the cell surface.

signal disappeared after about 20 min despite continued co-localization of phosphotyrosine labelling with EGFR-GFP in endosomal structures. But, immunoprecipitation experiments indicated that the EGFR remained phosphorylated under these conditions. This indicates that recruitment of other proteins to the activated receptors might have prevented the anti-phosphotyrosine antibody from directly binding the activated receptor. The result also implies that the internalized receptor continues to undergo sustained signalling. In the future, similar approaches should allow researchers to pinpoint protein activation and specific protein-protein interactions with high spatial and temporal resolution.Combining FRET measurements with assays for the reversible association of soluble proteins with cell membranes, a common event in many signalling pathways 70 , should also be informative.

Recently, FRET microscopy has also provided new insights into the structure of membrane microdomains known as lipid rafts. The lipid raft model suggests that cholesterol- and glycosphingolipid-enriched membrane microdomains organize certain proteins into functional domains during cell signalling and intracellular transport 71,72 . To what extent lipid raft domains concentrate membrane proteins under steady-state conditions is a controversial question that has been addressed by FRET microscopy 73-75 .A simple test to evaluate whether a given protein is clustered in a raft domain or not is to examine how energy-transfer efficiency between donor- and acceptor-labelled molecules changes as a function of their surface density (FIG. 5c). If the protein is clustered in a raft domain then FRET between individual proteins will be regulated by their packing in the raft domain. If instead the protein is just randomly distributed across the cell surface then the distance between molecules will decrease and FRET will increase as the surface density increases.Membrane proteins can get close enough to undergo substantial FRET when present at high concentrations.Using these criteria to define lipid rafts, one study observed FRET consistent with clustering 73 , but two others did not 74,75 .This inconsistency indicates that raft domains might be either easily perturbed or extremely small, perhaps containing only a few proteins at any given time under steady-state conditions.To act as functional units during intracellular transport or cell signalling, these otherwise small raft domains transiently coalesce into larger structures. Probing the size and dynamics of lipid rafts during these processes will be an important future application of FRET microscopy.

Fluorescence correlation spectroscopy.A technique that holds great promise in advancing future studies of protein-protein interactions in vivo is fluorescence correlation spectroscopy (FCS).FCS was first described over 30 years ago, but interest in this technique has undergone a recent resurgence 76-78 after several technical advances - especially the ability to define a very small sample volume (~1 femtolitre, 1 ×10 -15 l) using confocal microscopy - have increased its feasibility for live cells. Importantly, FCS measurements done using a confocal microscope can be made on fluorescently labelled proteins at any location within the cell.FCS measures the fluctuations in photons resulting from fluorescently labelled molecules diffusing in and out of a defined volume (reviewed in REFS 76-79) (FIG. 6).These fluctuations reflect the average number of fluorescently labelled molecules in the volume (which can be converted to concentrations), as well as the characteristic time of diffusion of each molecule across the confocal volume (which can be converted to diffusion constants).The amplitude of the AUTOCORRELATION FUNCTION of the fluctuations is inversely proportional to the average number of fluorescent objects and so constitutes an absolute in vivomeasurement of the concentration of these objects in the confocal volume 80 . FCS thus joins FRAP as another method to measure diffusion in intracellular compartments (TABLE 4).FCS is exquisitely sensitive, requiring extremely low concentrations of fluorophores (nanomolar concentrations), and is even sensitive to the photophysical properties of fluorophores. It can also readily detect several diffusing species, and can therefore be used as a sensitive probe of protein-protein interactions. For example,when a fluorescently labelled soluble ligand binds a larger (unlabelled) receptor, the diffusion of the complexed ligand will be slowed compared with the free ligand (FIG. 6).As FCS can detect the fraction of free and bound material, such measurements can be potentially used to calculate affinity constants in vivo (TABLE 2). In cases for which binding does not result in a large enough change in the diffusion times between the free and bound species, as measured by the correlation function (for example,when two soluble proteins with similar molecular weights bind one another), then TWOPHOTONdual-colour FCS is an alternative method that can be used to detect their interaction 81 . In this version of FCS, the two proteins of interest are labelled with different fluorophores, and cross-correlation analysis detects the bound labelled proteins as a single species. FCS also has more specialized applications that are discussed in detail elsewhere 76-79 .We are now at the earliest stages of using FCS in cells (TABLE 4),but given its ability to measure concentrations and diffusion constants, as well as to detect several diffusing species, it should provide a versatile addition to the tools we have described above.

| Table 4 &#124; Recent applications of fluorescence correlation spectroscopy   | Table 4 &#124; Recent applications of fluorescence correlation spectroscopy   |
|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| Application                                                                   | References                                                                    |
| Diffusional mobility in cells                                                 | Diffusional mobility in cells                                                 |
| Epidermal growth factor receptor                                              | 119                                                                           |
| Fluorescent dextran                                                           | 120,121                                                                       |
| EGFP                                                                          | 122                                                                           |
| EGFP-β-galactosidase                                                          | 122                                                                           |
| Fluorescent lipid analogues                                                   | 123                                                                           |
| Oligonucleotides                                                              | 124                                                                           |
| Protein transport                                                             | Protein transport                                                             |
| GFP in plastid tubules                                                        | 125                                                                           |
| Tubulin in squid axons                                                        | 126                                                                           |
| Binding interactions                                                          | Binding interactions                                                          |
| Proinsulin carboxy-peptide-cell membranes                                     | 127                                                                           |
| Ras-binding domain of Raf-1                                                   | 128                                                                           |
| GFP properties                                                                | 129,130                                                                       |

<!-- image -->

ATOMIC FORCE MICROSCOPY A microscope that nondestructively measures the forces (at the atomic level) between a sharp probing tip (which is attached to a cantilever spring) and a sample surface. The microscope images structures at the resolution of individual atoms.

## 4-PI MICROSCOPE

A microscope that combines the wavefronts produced by two opposed high-aperture lenses and a two-photon excitation laser to allow three-dimensional imaging of transparent biological specimens with an axial resolution in the 100-140nm range.

## STIMULATED EMISSION MICROSCOPE

(Also referred to as ultrafastdynamics microscope).A light microscope that increases the spatial resolution of a fluorescent sample by exciting the fluorophore with a femtosecond laser pulse followed by a quenching timedelayed red-shifted femtosecond laser pulse that depletes fluorescence at the focal rim surrounding the focal volume.

## Perspective

We are at the beginning of a new era in the study of protein dynamics and interactions within cells.Much progress is to be expected with developments in GFP technology and other fluorescent labelling systems, as well as in microscopic techniques.There is still much to learn about the complex properties of GFP. As we begin to understand these properties, new applications of GFP are likely to become available 2,7 ; for example, some forms of GFP can be photoactivated by a brief burst of high frequency laser light 2,82,83 . If this behaviour could be further optimized, the resulting GFP variant could be useful for following populations of photoactivated fluorescent molecules over time with minimal background noise.Optical shifting, blinking, or on/off switching have been observed for wild-type GFP, red-shifted GFP, yellow variants of GFP and the S65T GFP mutant 84,85 , and could potentially be exploited in useful ways in the future.Alternatives to GFP for labelling proteins in living cells are also available. These include two recent developments, fluorescein arsenical helix binder (FLASH) and SINGLE-CHAIN ANTIBODIES. FLASH is a membrane-permeable fluorophore that binds to a five amino-acid peptide engineered into a protein of interest 86 . Single-chain antibodies use a related approach.An organelle-targeting sequence is fused to a single-chain antibody and expressed in a cell.A membrane-permeable fluorescently tagged peptide sequence with high affinity for the antibody is incubated with the cells and results in specific labelling of a compartment of interest 87 .

Developments in modern imaging approaches are keeping pace with these advances in fluorescent labelling of proteins. It is possible to combine microscopic approaches, including: FRAP and TOTAL INTERNAL

1. Matz, M. V. et al. Fluorescent proteins from nonbioluminescent Anthozoa species. Nature Biotechnol. 17, 969-973 (1999); erratum 17, 1227 (1999).
2. Tsien, R. Y. The green fluorescent protein. Annu. Rev. Biochem. 67, 509-544 (1998).
3. Heim, R., Prasher, D. C. &amp; Tsien, R. Y. Wavelength mutations and posttranslational autoxidation of green fluorescent protein. Proc. Natl Acad. Sci. USA 91, 12501-12504 (1994).
4. Swaminathan, R., Hoang, C. P. &amp; Verkman, A. S. Photobleaching recovery and anisotropy decay of green fluorescent protein GFP-S65T in solution and cells: cytoplasmic viscosity probed by green fluorescent protein translational and rotational diffusion. Biophys. J. 72, 1900-1907 (1997).

Characterizes the photobleaching properties of GFP in solution and in vivo in the cytoplasm.

5. Lippincott-Schwartz, J. et al. in Green Fluorescent Proteins (eds Sullivan, K. &amp; Kay, S.) 261-291 (Academic, San Diego, 1999).
6. Yang, F., Moss, L. G. &amp; Phillips, G. N. J. The molecular structure of green fluorescent protein. Nature Biotechnol. 14, 1246-1251 (1996).
7. Prendergast, F. G. Biophysics of the green fluorescent protein. Methods Cell Biol. 58, 1-18 (1999).
8. Axelrod, D., Koppel, D. E., Schlessinger, J., Elson, E. &amp; Webb, W. W. Mobility measurement by analysis of fluorescence photobleaching recovery kinetics. Biophys. J. 16, 1055-1069 (1976).
9. White, J. &amp; Stelzer, E. Photobleaching GFP reveals protein dynamics inside living cells. Trends Cell Biol. 9, 61-65 (1999).
10. Saxton, M. J. &amp; Jacobsen, K. Single-particle tracking: applications to membrane dynamics. Annu. Rev. Biophys.

Biomol. Struct. 26, 373-399 (1997).

REFLECTION MICROSCOPY to measure events close to the plasma membrane 88-90 ; MULTIPHOTON MICROSCOPY and FRAP to study protein movement in deep tissue 91 ; IMAGE CORRELATION SPECTROSCOPY of laser scanning confocal images to analyse membrane protein cluster densities and sizes 92 ; and FRET and ATOMIC FORCE MICROSCOPY to obtain a high-resolution three-dimensional map of protein interaction patterns 93 .Moreover, light microscopes with improved resolution are available, including the 4-PI and the STIMULATED EMISSION MICROSCOPES 94,95 ,which increase resolution by factors of two- to fivefold over the theoretical limit. Increased resolving power could permit analysis of protein dynamics within subcompartments of, at present, unresolvable organelles such as the Golgi cisterna or within smaller organisms such as yeast and bacteria. Economical supercomputers, new fluorescent proteins, and high-throughput screening methods will allow for even more sophisticated and expansive studies. These advances are helping researchers move from a steady-state view of protein distribution and function in cells to a dynamic model that integrates information on protein localization, concentration, diffusion and interactions that are indiscernible from protein sequences and in vitrobiochemical experiments.

<!-- image -->

## Links

DATABASE LINKS high mobility group 17 | ASF | fibrillarin | protein kinase Cα | Fas | FasL | tumour necrosis factor receptor 1 | tumour necrosis factor

FURTHER INFORMATIONCompact barrel-like structure

receptor 2 | EGFR of GFP | Lippincott-Schwartz lab

ENCYCLOPEDIA OF LIFE SCIENCESGreen fluorescent protein | Fluorescence microscopy | Fluorescence resonance energy transfer

2722-2730 (1998).

11. Edidin, M. in Mobility and Proximity in Biological Membranes (eds Edidin, M., Szollosi, J. &amp; Tron, L.) 109-135 (CRC Press, Boca Raton, Florida, 1994).
12. Feder, T. J., Brust-Mascher, I., Slattery, J. P., Baird, B. &amp; Webb, W. W. Constrained diffusion or immobile fraction on cell surfaces: a new interpretation. Biophys. J. 70, 2767-2773 (1996).
13. Ellenberg, J. et al. Nuclear membrane dynamics and reassembly in living cells: targeting of an inner nuclear
4. membrane protein in interphase and mitosis. J. Cell Biol. 138, 1193-1206 (1997). Shows the connectivity of the endoplasmic reticulum (ER) and nuclear envelope in vivo and provides a visual example of how a protein can be mobile in one domain of the cell and immobile in another domain.
14. Edidin, M. in The Structure of Biological Membranes (ed. Yeagle, P.) 539-572 (CRC, Boca Raton, 1992) .
15. Cole, N. B. et al. Diffusional mobility of Golgi proteins in membranes of living cells. Science 273, 797-801 (1996). First paper to use FRAP to measure the diffusion rate of a GFP chimaera in a cellular organelle, the Golgi. In addition, this paper introduces the FLIP method of photobleaching.
16. Sciaky, N. et al. Golgi tubule traffic and the effects of brefeldin A visualized in living cells. J. Cell Biol. 139, 1137-1155 (1997).
17. Partikian, A., Olveczky, B., Swaminathan, R., Li, Y. &amp; Verkman, A. S. Rapid diffusion of green fluorescent protein in the mitochondrial matrix. J. Cell Biol. 140, 821-829 (1998).
18. Olveczky, B. P. &amp; Verkman, A. S. Monte Carlo analysis of obstructed diffusion in three dimensions: application to molecular diffusion in organelles. Biophys. J. 74,
19. Siggia, E. D., Lippincott-Schwartz, J. &amp; Bekiranov, S. Diffusion in an inhomogeneous media: theory and simulations applied to a whole cell photobleach recovery. Biophys. J. 79, 1761-1770 (2000). Describes a simulation program that can be used to
11. calculate diffusion rates from FRAP data obtained by a confocal microscope.
20. Dayel, M. J., Hom, E. F. Y. &amp; Verkman, A. S. Diffusion of green fluorescent protein in the aqueous-phase lumen of endoplasmic reticulum. Biophys. J. 76, 2843-2851 (1999).
21. Phair, R. D. &amp; Misteli, T. High mobility of proteins in the mammalian cell nucleus. Nature 404, 604-609 (2000). The relatively slow diffusion rates of several nuclear GFP chimaeras are due to the high density of binding sites for the chimaeras throughout the nucleus. A kinetic model of the protein dynamics is used to calculate the on/off rates of chimaera binding.
22. Gordon, G. W., Chazotte, B., Wang, X. F. &amp; Herman, B. Analysis of simulated and experimental fluorescence recovery after photobleaching. Data for two diffusing components. Biophys. J. 68, 766-778 (1995).
23. Periasamy, N. &amp; Verkman, A. S. Analysis of fluorophore diffusion by continous distributions of diffusion coefficients: application to photobleaching measurements of multicomponent and anomalous diffusion. Biophys. J. 75, 557-567 (1998).
24. Kruhlak, M. J. et al. Reduced mobility of the alternate splicing factor (ASF) through the nucleoplasm and steady state speckle compartments. J. Cell Biol. 150, 41-51 (2000).
25. Houtsmuller, A. B. et al. Action of DNA repair endonuclease ERCC1/XPF in living cells. Science 284, 958-961 (2000).
26. Poo, M. M. &amp; Cone, R. A. Lateral diffusion of rhodopsin in

<!-- image -->

the photoreceptor membrane. Nature 247, 438-441 (1974).

27. Marguet, D. et al. Lateral diffusion of GFP-tagged H2Ld molecules and of GFP-TAP1 reports on the assemby and retention of these molecules in the endoplasmic reticulum. Immunity 11, 231-240 (1999).

Characterizes the effect of the formation of large protein complexes of TAP and MHC class I in the ER membrane on the diffusion rate, and calculates the relative contributions of several diffusing species to

- a single apparent diffusion coefficient.
28. Zaal, K. J. M. et al. Golgi membranes are absorbed into and reemerge from the ER during mitosis. Cell 99, 589-601 (1999).

Uses FRAP to measure the mobilty of a Golgi membrane protein during interphase and metaphase to test whether the Golgi fragments or fuses with the endoplasmic reticulum during mitosis. In addition, selective photobleaching is used to calculate the relative rates of transport between the ER and Golgi in both directions.

29. Saxton, M. Anomalous diffusion due to obstacles: a Monte Carlo study. Biophys. J. 66, 394-401 (1994).
30. Saxton, M. Anomalous diffusion due to binding: a Monte Carlo study. Biophys. J. 70, 1250-1262 (1996).
31. Adams, C. L., Chen, Y., Smith, S. J. &amp; Nelson, W. J. Mechanisms of epithelial cell-cell adhesion and cell compaction revealed by high-resolution tracking of Ecadherin-green fluorescent-protein. J. Cell Biol. 142, 1105-1119 (1998).
32. Nehls, S. et al. Dynamics and retention of misfolded proteins in native ER membranes. Nature Cell Biol. 2, 288-295 (2000). The diffusion rates and mobility of misfolded aggregated ER membrane proteins are compared to correctly folded proteins and are found to be similar. Only conditions that globally perturb folding in the ER were found to have an effect on protein mobility.
33. Subramanian, K. &amp; Meyer, T. Calcium-induced restructuring of nuclear envelope and endoplasmic reticulum calcium stores. Cell 89, 963-971 (1997).
34. Terasaki, M., Jaffe, L. A., Hunnicutt, G. R. &amp; Hammer, J. A. R. Structural change of the endoplasmic reticulum during fertilization: evidence for loss of membrane continuity using the green fluorescent protein. Dev. Biol. 179, 320-328 (1996).
35. Kohler, R. H., Cao, J., Zipfel, W. R., Webb, W. W. &amp; Hanson, M. R. Exchange of protein molecules through connections between higher plastids. Science 276, 2039-2042 (1997).
36. Storrie, B. et al. Recycling of Golgi-resident glycosyltransferases through the ER reveals a novel pathway and provides an explanation for nocodazoleinduced Golgi scattering. J. Cell Biol. 143, 1505-1521 (1998).
37. Presley, J. F., Miller, C., Zaal, K., Ellenberg, J. &amp; Lippincott-Schwartz, J. In vivo dynamics of COPI. Mol. Biol. Cell 9, S746 (1998).
38. Stephens, D. J., Lin-Marq, N., Pagano, A., Pepperkok, R. &amp; Paccaud, J. P. COPI-coated ER-to-Golgi transport complexes segregate form COPII in close proximity to ER exit sites. J. Cell Sci. 113, 2177-2185 (2000).
39. Vasudevan, C. et al. The distribution and translocation of the G protein ADP-ribosylation factor 1 in live cells is determined by its GTPase activity. J. Cell Sci. 111, 1277-1285 (1998).
40. Oancea, E., Teruel, M. N., Quest, A. F. &amp; Meyer, T. Green fluorescent protein (GFP)-tagged cysteine-rich domains from protein kinase C as fluorescent indicators of diacylglycerol signaling in living cells. J. Cell Biol. 140, 485-498 (1998).
41. Reits, E. A., Benham, A. M., Plougastel, B., Neefjes, J. &amp; Trowsdale, J. Dynamics of the proteasome distribution in living cells. EMBO J. 16, 6087-6094 (1997).
42. Presley, J. F. et al. ER-to-Golgi transport visualized in living cells. Nature 389, 81-85 (1997).
43. Hirschberg, K. et al. Kinetic analysis of secretory protein traffic and characterization of Golgi to plasma membrane transport intermediates in living cells. J. Cell Biol. 143, 1485-1503 (1998).
44. Nakata, T., Terada, S. &amp; Hirokawa, N. Visualization of the dynamics of synaptic vesicle and plasma membrane proteins in living axons. J. Cell Biol. 140, 659-674 (1998).
45. Wu, P. &amp; Brand, L. Resonance energy transfer: methods and applications. Anal. Biochem. 218, 1-13 (1994).
46. Clegg, R. M. Fluorescence resonance energy transfer. Curr. Opin. Biotechnol. 6, 103-110 (1995).
47. Patterson, G. H., Piston, D. W. &amp; Barisas, B. G. Förster distances between green fluorescent protein pairs. Anal.

Biochem. 284, 438-440 (2000).

48. Pollok, B. A. &amp; Heim, R. Using GFP in FRET-based applications. Trends Cell Biol. 9, 57-60 (1999).
49. Periasamy, A. &amp; Day, R. N. Visualizing protein interactions in living cells using digitized GFP imaging and FRET microscopy. Methods Cell Biol. 58, 293-314 (1999).
50. Heim, R. &amp; Tsien, R. Y. Engineering green fluorescent protein for improved brightness, longer wavelengths and fluorescence resonance energy transfer. Curr. Biol. 6, 178-182 (1996).
51. Bastiaens, P. I. H. &amp; Jovin, T. M. in Cell Biology: A Laboratory Handbook (ed. Celis, J. E.) 136-146 (Academic, New York, 1998).
52. Wouters, F. S. &amp; Bastiaens, P. I. Fluorescence lifetime imaging of receptor tyrosine kinase activity in cells. Curr. Biol. 9, 1127-1130 (1999). Describes a clever assay to evaluate the phosphorylation state of a protein using FRET.
53. Bastiaens, P. I. &amp; Squire, A. Fluorescence lifetime imaging microscopy: spatial resolution of biochemical processes in the cell. Trends Cell Biol. 9, 48-52 (1999).
54. Ng, T. et al. Imaging protein kinase Cα activation in cells. Science 283, 2085-2089 (1999).
55. Ng, T. et al. PKCα regulates β1 intergrin-dependent cell motility through association and control of integrin traffic. EMBO J. 18, 3909-3923 (1999).
56. Emmanouilidou, E. et al. Imaging Ca 2+ concentration changes at the secretory vesicle surface with a recombinant targeted cameleon. Curr. Biol. 9, 915-918 (1999).
57. Romoser, V. A., Hinkle, P. M. &amp; Persechini, A. Detection in living cells of Ca 2+ -dependent changes in the fluorescence emission of an indicator composed of two green fluorescent protein variants linked by a calmodulin-binding sequence. A new class of fluorescent indicators. J. Biol. Chem. 272, 13270-13274 (1997).
58. Miyawaki, A. et al. Fluorescent indicators for Ca 2+ based on green fluorescent proteins and calmodulin. Nature 388, 882-887 (1997).
59. Zaccolo, M. et al. A genetically encoded, fluorescent indicator for cyclic AMP in living cells. Nature Cell Biol. 2, 25-29 (2000).
60. Honda, A. et al. Spatiotemporal dynamics of guanosine 3',5'-cyclic monophosphate revealed by a genetically encoded, fluorescent indicator. Proc. Natl Acad. Sci. USA 98, 2437-2442 (2001).
61. Mitra, R. D., Silva, C. M. &amp; Youvan, D. C. Fluorescence resonance energy transfer between blue-emitting and redshifted excitation derivatives of the green fluorescent protein. Gene 173, 13-17 (1996).
62. Mahajan, N. P., Harrison-Shostak, D. C., Michaux, J. &amp; Herman, B. Novel mutant green fluorescent protein protease substrates reveal the activation of specific caspases during apoptosis. Chem. Biol. 6, 401-409 (1999).
63. Sagot, I., Bonneu, M., Balguerie, A. &amp; Aigle, M. Imaging fluorescence resonance energy transfer between two green fluorescent proteins in living yeast. FEBS Lett. 447, 53-57 (1999).
64. Vanderklish, P. W. et al. Marking synaptic activity in dendritic spines with a calpain substrate exhibiting fluorescence resonance energy transfer. Proc. Natl Acad. Sci. USA 97, 2253-2258 (2000).
65. Xu, X. et al. Detection of programmed cell death using fluorescence energy transfer. Nucleic Acids Res. 26, 2034-2035 (1998).
66. Zlokarnik, G. et al. Quantitation of transcription and clonal selection of single living cells with β-lactamase as reporter. Science 279, 84-88 (1998).
67. Xu, Y., Piston, D. W. &amp; Johnson, C. H. A bioluminescence resonance energy transfer (BRET) system: application to interacting circadian clock proteins. Proc. Natl Acad. Sci. USA 96, 151-156 (1999).
68. Siegel, R. M. et al. Fas preassociation required for apoptosis signaling and dominant inhibition by pathogenic mutations. Science 288, 2354-2357 (2000).
69. Chan, F. K.-M. et al. A domain in TNF receptors that mediates ligand-independent receptor assembly and signaling. Science 288, 2351-2354 (2000).
70. Teruel, M. N. &amp; Meyer, T. Translocation and reversible localization of signaling proteins: a dynamic future for signal transduction. Cell 103, 181-184 (2000).
71. Simons, K. &amp; Ikonen, E. Functional rafts in cell membranes. Nature 387, 569-572 (1997).
72. Simons, K. &amp; Toomre, D. Lipid rafts and signal transduction. Nature Rev. Mol. Cell Biol. 1, 31-39 (2000).
73. Varma, R. &amp; Mayor, S. GPI-anchored proteins are organized in submicron domains at the cell surface. Nature 394, 798-801 (1998).

Uses a variation of FRET, homotransfer, to infer the structure of lipid rafts on the cell surface.

74. Kenworthy, A. K. &amp; Edidin, M. Distribution of a glycosylphosphatidylinositol-anchored protein at the apical surface of MDCK cells examined at a resolution of &lt;100 Å using imaging fluorescence resonance energy transfer. J. Cell Biol. 142, 69-84 (1998).

Uses acceptor photobleaching FRET to assess the organization of lipid rafts at the cell surface. Contains a detailed discussion of the theory for interpreting FRET from donors and acceptors constrained to membranes.

75. Kenworthy, A. K., Petranova, N. &amp; Edidin, M. Highresolution FRET microscopy of cholera toxin B-subunit and GPI-anchored proteins in cell plasma membranes. Mol. Biol. Cell 11, 1645-1655 (2000).
76. Rigler, R. &amp; Elson, E. S. Fluorescence Correlation Spectroscopy (Springer, New York, 2001).
77. Maiti, S., Haupts, V. &amp; Webb, W. W. Fluorescence correlation spectroscopy: diagnostics for sparse molecules. Proc. Natl Acad. Sci. USA 94, 11753-11757 (1997).
78. Eigen, M. &amp; Rigler, R. Sorting single molecules: application to diagnostics and evolutionary biotechnology. Proc. Natl Acad. Sci. USA 91, 5740-5747 (1994).
79. Van Craenenbroeck, E. &amp; Engelborghs, Y. Fluorescence correlation spectroscopy: molecular recognition at the single molecule level. J. Mol. Recog. 13, 93-100 (2000).
80. Cluzel, P., Surette, M. &amp; Leibler, S. An ultrasensitive bacterial motor revealed by monitoring signaling proteins in single cells. Science 287, 1652-1655 (2000).
81. Heinze, K. G., Koltermann, A. &amp; Schwille, P. Simultaneous two-photon excitation of distinct labels for dual-color fluorescence crosscorrelation analysis. Proc. Natl Acad. Sci. USA 97, 10377-10382 (2000).
82. Elowitz, M. B., Surette, M. G., Wolf, P. E., Stock, J. &amp; Leibler, S. Photoactivation turns green fluorescent protein red. Curr. Biol. 7, 809-812 (1997).
83. Yokoe, H. &amp; Meyer, T. Spatial dynamics of GFP-tagged proteins investigated by local fluorescence enhancement. Nature Biotechnol. 14, 1252-1256 (1996).
84. Creemers, T. H., Lock, A. J., Subramaniam, V., Jovin, T. M. &amp; Volker, S. Photophysics and optical switching in green fluorescent protein mutants. Proc. Natl Acad. Sci. USA 97, 2974-2978 (2000).
85. Dickson, R. M., Cubitt, A. B., Tsien, R. Y. &amp; Moerner, W. E. On/off blinking and switching behaviour of single molecules of green fluorescent protein. Nature 388, 355-358 (1997).
86. Griffin, B. A., Adams, S. R. &amp; Tsien, R. Y. Specific covalent labeling of recombinant protein molecules inside live cells. Science 281, 269-272 (1998).
87. Farinas, J. &amp; Verkman, A. S. Receptor-mediated targeting of fluorescent probes in living cells. J. Biol. Chem. 274, 7603-7606 (1999).
88. Sund, S. E. &amp; Axelrod, D. Actin dynamics at the living cell submembrane imaged by total internal reflection fluorescence photobleaching. Biophys. J. 79, 1655-1669 (2000).
89. Toomre, D. K., Steyer, J. A., Almers, W. &amp; Simons, K. Observing fusion of constitutive membrane traffic in real time by evanescent wave microscopy. J. Cell Biol. 149, 33-40 (2000).
90. Schmoranzer, J., Goulian, M., Axelrod, D. &amp; Simon, S. M. Imaging constitutive exocytosis with total internal reflection fluorescence microscopy. J. Cell Biol. 149, 23-32 (2000).
91. Brown, E. B., Wu, E. S., Zipfel, W. &amp; Webb, W. W. Measurement of molecular diffusion in solution by multiphoton fluorescence photobleaching recovery. Biophys. J. 77, 2837-2849 (1999).
92. Petersen, N. O. et al. Analysis of membrane protein cluster densities and sizes in situ by image correlation spectroscopy. Faraday Discuss. 289-305; discussion 331-343 (1998).
93. Subramaniam, V., Kirsch, A. K. &amp; Jovin, T. M. Cell biological applications of scanning near-field optical microscopy (SNOM). Cell. Mol. Biol. 44, 689-700 (1998).
94. Klar, T., Jakobs, S., Dyba, M., Egner, A. &amp; Hell, S. Fluorescence microscopy with diffraction resolution barrier broken by stimulated emission. Proc. Natl Acad. Sci. USA 97, 8206-8210 (2000).
95. Nagorni, M. &amp; Hell, S. W. 4Pi-confocal microscopy provides three-dimensional images of the microtubule network with 100- to 150-nm resolution. J. Struct. Biol. 123, 236-247 (1998).
96. Patterson, G. H., Knobel, S. M., Sharif, W. D., Kain, S. R. &amp; Piston, D. W. Use of green fluorescent protein and its mutants in quantitative fluorescence microscopy. Biophys. J. 73, 2782-2790 (1997).
97. Baird, G. S., Zacharias, D. A. &amp; Tsien, R. Y. Biochemistry,

<!-- image -->

## RE V I EWS

- mutagenesis, and oligomerization of DsRed, a red fluorescent protein from coral. Proc. Natl Acad. Sci. USA 97, 11984-11989 (2000).
98. Dictenberg, J. B. et al. Pericentrin and γ-tubulin form a protein complex and are organized into a novel lattice at the centrosome. J. Cell Biol. 141, 163-174 (1998).
99. Bastiaens, P. I., Majoul, I. V., Verveer, P. J., Soling, H. D. &amp; Jovin, T. M. Imaging the intracellular trafficking and state of the AB5 quaternary structure of cholera toxin. EMBO J. 15, 4246-4253 (1996).
100. Damjanovich, S. et al. Structural hierarchy in the clustering of HLA class I molecules in the plasma membrane of human lymphoblastoid cells. Proc. Natl Acad. Sci. USA 92, 1122-1126 (1995).
101. Jovin, T. M. &amp; Arndt-Jovin, D. J. in Cell Structure and Function by Microspectrofluorimetry (eds Kohen, E., Ploem, J. S. &amp; Hirschberg, J. G.) 99-117 (Academic, Orlando, Florida,1989).
102. Nagai, Y. et al. A fluorescent indicator for visualizing cAMPinduced phosphorylation in vivo. Nature Biotechnol. 18, 313-316 (2000).
103. Kam, Z., Volberg, T. &amp; Geiger, B. Mapping of adherens junction components using microscopic resonance energy transfer imaging. J. Cell Sci. 108, 1051-1062 (1995). An elegant FRET microscopy study using immunofluorescence labelling to probe the distribution of proteins in adherens junctions.
104. Xia, Z., Zhou, Q., Lin, J. &amp; Liu, Y. Stable SNARE complex prior to evoked synaptic vesicle fusion revealed by fluorescence resonance energy transfer. J. Biol. Chem. 276, 1766-1771 (2001).
105. Wouters, F. S., Bastiaens, P. I. H., Wirtz, K. W. A. &amp; Jovin, T. M. FRET microscopy demonstrates molecular assocation of non-specific lipid transfer protein (nsL-TP) with fatty acid oxidation enzymes in peroxisomes. EMBO J. 17, 7179-7189 (1998).
106. Bacsó, Z., Bene, L., Bodnár, A., Matkó, J. &amp; Damjanovich, S. A photobleaching energy transfer analysis of CD8/MHCI and LFA-1/ICAM-1 interactions in CTL-target cell conjugates. Immunol. Lett. 54, 151-156 (1996).
107. Gadella, T. W. Jr &amp; Jovin, T. M. Oligomerization of epidermal growth factor receptors on A431 cells studied by time-resolved fluorescence imaging microscopy. A stereochemical model for tyrosine kinase receptor activation. J. Cell Biol. 129, 1543-1558 (1995).
108. Sako, Y., Minoghchi, S. &amp; Yanagida, T. Single-molecule imaging of EGFR signalling on the surface of living cells.
- Nature Cell Biol. 2, 168-172 (2000). Combines single-molecule fluorescence techniques, total internal reflection microscopy, and FRET to follow the dimerization of the EGFR upon EGF binding.
109. Angers, S. et al. Detection of β2-adrenergic receptor
- dimerization in living cells using bioluminescence resonance energy transfer (BRET). Proc. Natl Acad. Sci. USA 97, 3684-3689 (2000).
110. Schütz, G. J., Kada, G., Pastushenko, V. P. &amp; Schindler, H. Propeties of lipid microdomains in a muscle cell membrane visualized by single molecule microscopy. EMBO J. 19, 892-901 (2000).
111. Mahajan, N. P. et al. Bcl-2 and Bax interactions in mitochondria probed with green fluorescent protein and fluorescence resonance energy transfer. Nature Biotechnol. 16, 547-552 (1998).
112. Ruehr, M. L., Zakhary, D. R., Damron, D. S. &amp; Bond, M. Cyclic AMP-dependent protein kinase binding to A-kinase anchoring proteins in living cells by fluorescence resonance energy transfer of green fluorescent protein fusion proteins. J. Biol. Chem. 274, 33092-33096 (1999).
113. Kindzelskii, A. L., Yang, Z., Nabel, G. J., Todd, R. F. R. &amp; Petty, H. R. Ebola virus secretory glycoprotein (sGP) diminishes Fcγ RIIIB-to-CR3 proximity on neutrophils. J. Immunol. 164, 953-958 (2000).
114. Damelin, M. &amp; Silver, P. A. Mapping interactions between nuclear transport factors in living cells reveals pathways through the nuclear pore complex. Mol. Cell 5, 133-140
- (2000). Novel interactions between nuclear transport factors and nucleoporins are revealed in a FRET-based protein-protein interaction screen in yeast.
115. Day, R. N. Visualization of Pit-1 transcription factor interactions in the living cell nucleus by fluorescence resonance energy transfer microscopy. Mol. Endocrinol. 12, 1410-1419 (1998).
116. Schmid, J. A. et al. Dynamics of NF-κB and IκBα studied with green fluorescent protein (GFP) fusion proteins. Investigation of GFP-p65 binding to DNA by fluorescence resonance energy transfer. J. Biol. Chem. 275, 17035-17042 (2000).
117. Llopis, J. et al. Ligand-dependent interactions of coactivators steroid receptor coactivator-1 and peroxisome proliferator-activated receptor binding protein with nuclear hormone receptors can be imaged in live cells and are required for transcription. Proc. Natl Acad. Sci. USA 97, 4363-4368 (2000); erratum 97, 9819 (2000).
118. Prufer, K., Racz, A., Lin, G. C. &amp; Barsony, J. Dimerization with retinoid X receptors promotes nuclear localization and subnuclear targeting of vitamin D receptors. J. Biol. Chem. 275, 41114-41123 (2000).
119. Brock, R., Vamosi, G., Vereb, G. &amp; Jovin, T. M. Rapid characterization of green fluorescent protein fusion proteins on the molecular and cellular level by fluorescence correlation microscopy. Proc. Natl Acad. Sci. USA 96, 10123-10128 (1999).

Provides a concise overview of how FCS and

- confocal microscopy can be linked to study the diffusional mobility of GFP-tagged proteins in cells.
120. Brock, R. &amp; Jovin, T. M. Fluorescence correlation microscopy (FCM)-fluorescence correlation spectroscopy (FCS) taken into the cell. Cell Mol. Biol. 44, 847-856 (1998).
121. Brock, R., Hink, M. A. &amp; Jovin, T. M. Fluorescence correlation microscopy of cells in the presence of autofluorescence. Biophys. J. 75, 2547-2557 (1998).
122. Wachsmuth, M., Waldeck, W. &amp; Langowski, J. Anomalous diffusion of fluorescent probes inside living cell nuclei investigated by spatially-resolved fluorescence correlation spectroscopy. J. Mol. Biol. 298, 677-689 (2000).
123. Schwille, P., Korlach, J. &amp; Webb, W. W. Fluorescence correlation spectroscopy with single-molecule sensitivity on cell and model membranes. Cytometry 36, 176-182 (1999).
124. Politz, J. C., Browne, E. S., Wolf, D. E. &amp; Pederson, T. Intranuclear diffusion and hybridization state of oligonucleotides measured by fluorescence correlation spectroscopy in living cells. Proc. Natl Acad. Sci. USA 95, 6043-6048 (1998).
125. Köhler, R. H., Schwille, P., Webb, W. W. &amp; Hanson, M. R. Active protein transport through plastid tubles: velocity quantified by fluorescence correlation spectroscopy. J. Cell Sci. 113, 3921-3930 (2000).
126. Terada, S., Kinjo, M. &amp; Hirokawa, N. Oligomeric tubulin in large transporting complex is transported via kinesin in squid giant axons. Cell 103, 141-155 (2000).
127. Rigler, R. et al. Specific binding of proinsulin C-peptide to human cell membranes. Proc. Natl Acad. Sci. USA 96, 13318-13323 (1999).
128. Trier, U., Olah, Z., Kleuser, B. &amp; Schafer-Korting, M. Fusion of the binding domain of Raf-1 kinase with green fluorescent protein for activated Ras detection by fluorescence correlation spectroscopy. Pharmazie 54, 263-268 (1999).
129. Terry, B. R., Matthews, E. K. &amp; Haseloff, J. Molecular characterisation of recombinant green fluorescent protein by fluorescence correlation microscopy. Biochem. Biophys. Res. Commun. 217, 21-27 (1995).
130. Haupts, U., Maiti, S., Schwille, P. &amp; Webb, W. W. Dynamics of fluorescence fluctuations in green fluorescent protein observed by fluorescence correlation spectroscopy. Proc. Natl Acad. Sci. USA 95, 13573-13578 (1998).

## Acknowledgements

We thank members of the Lippincott-Schwartz laboratory for helpful comments on the manuscript. We also thank Gregoire Bonnet for useful discussions on fluorescence correlation spectroscopy. Anne Kenworthy was supported by a National Research Council-NICHD Research Associateship. Erik Snapp was supported by a PRAT Fellowship.

<!-- image -->