# VLL Gridpack Generation

This repository contains a suite of automation tools and templates for generating `MadGraph5_aMCatNLO` gridpacks for vector-like leptons within the CMS experiment. It supports both Run2 UltraLegacy (UL) and Run3 configurations.

### Directory Structure
```
.
├── Run3/                     # Run3 genproductions area
├── Run2UL/                   # Run2 UL genproductions area
├── templates/                # Data templates for MadGraph cards
├── modeldict.yaml            # Signal model & mass point definitions
├── generate_cards.py         # Card generation script
├── move_cards.py             # Script to sync cards to genproductions
└── generate_one_gridpack.py  # Automation for gridpack production
```

### Instructions

Edit `modeldict.yaml` to define the VLL scenarios. Clone the CMS `genproductions` tool into era-specific directories.
- For Run3:
  ```bash
  mkdir Run3 && cd Run3
  git clone https://github.com/cms-sw/genproductions.git --depth=1
  ```
- For Run2 UL:
  ```bash
  mkdir Run2UL && cd Run2UL
  git clone https://github.com/cms-sw/genproductions.git --depth=1 -b mg265UL
  ```

Card generation for mass points and moving them into the respective `genproductions` subdirectory:
```bash
python3 generate_cards.py --run [Run3/Run2UL]
python3 move_cards.py --run [Run3/Run2UL]
```
Gridpack generation using one script:
```bash
python3 generate_one_gridpack.py --run [Run3/Run2UL] --name VLLS_ele_M115 [--dryrun]
```
### Notes
This setup works with the following CMSSW versions and SCRAM ARCH. Make sure to run this in the compatible `lxplus` version.

| Run  | SCRAM_ARCH          | CMSSW version   |
|------|---------------------|-----------------|
| Run2 | `slc7_amd64_gcc700` | `CMSSW_10_6_26` |
| Run3 | `el8_amd64_gcc12`   | `CMSSW_13_0_13` |

For low mass points (e.g., M=100 GeV), certain decay chains like VLL -> Higgs + lepton may not be kinematically allowed if the Higgs is on-shell (Mh ~ 125 GeV). MadGraph may fail during the compilation of these subprocesses. It is recommended to skip these points or modify the decay logic if they are not critical. Ensure that the BSM model (`VLL.tgz`) is available in the central [cms-project-generators](https://cms-project-generators.web.cern.ch/cms-project-generators/) repository or correctly referenced in the `extramodels.dat` card.

----------

_Developed for the analysis **CMS-NPS-25-011** (Search for vector-like leptons in mulitlepton final states)_
