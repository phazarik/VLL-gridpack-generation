# #####################################################################################
# Script: generate_cards.py
# Purpose: Generates MadGraph cards (proc, customize, extramodels, run) based on 
#          a YAML model configuration and templates.
# Usage: python3 generate_cards.py --run Run3
# #####################################################################################

import os
import yaml
import argparse

## Handle --run argument
def normalize_run(value):
    val_lower = str(value).lower()
    if   val_lower in ['run3', '3']:           return 'Run3'
    elif val_lower in ['run2ul', 'run2', '2']: return 'Run2UL'
    return value
parser = argparse.ArgumentParser(description="Generate VLL MadGraph cards.")
parser.add_argument('--run', type=normalize_run, required=True, help="Era: Run3 or Run2UL")
args = parser.parse_args()

## Load templates and dict
with open("modeldict.yaml") as f: modeldict = yaml.safe_load(f)
with open("templates/proc_card_singlet.dat") as f: proc_singlet_template = f.read()
with open("templates/proc_card_doublet.dat") as f: proc_doublet_template = f.read()
with open("templates/extramodels.dat") as f:       extramodels_template  = f.read()
with open("templates/customizecards.dat") as f:    customize_template    = f.read()
with open("templates/run_card.dat") as f:          run_card_template     = f.read()

isospin_map = {"singlet": "0", "doublet": "-0.5"}

## Configure parameters based on Run
run = args.run
if run == 'Run3':
    proton_E = 6800
    dump = 'cards_Run3'
else:
    proton_E = 6500
    dump = 'cards_Run2UL'

count = 0
for tag, info in modeldict.items():

    ## put exceptions here
    if "VLLS" not in tag: continue
    
    model = info["model"]
    tarfile = info["tarfile"]
    coupling = info["coupling"]
    masses = info["masses"]
    isospin = isospin_map[info["type"]]

    ## Decay logic
    if   coupling == "mu":  decay_lep, decay_nu = "mu+ mu-", "vm vm~"
    elif coupling == "ele": decay_lep, decay_nu = "e+ e-", "ve ve~"
    elif coupling == "tau": decay_lep, decay_nu = "ta+ ta-", "vt vt~"
    else:
        decay_lep = "e+ e- mu+ mu- ta+ ta-"
        decay_nu  = "ve ve~ vm vm~ vt vt~"

    for mass in masses:
        count += 1
        prefix = f"{tag}_M{mass}"
        outdir = os.path.join(dump, prefix)
        os.makedirs(outdir, exist_ok=True)

        print(f"{count}. Processing cards for: {prefix} .. ", end='\t')

        ## Generate proc_card
        template = proc_singlet_template if info["type"] == "singlet" else proc_doublet_template
        proc = template.format(model=model, decay_lep=decay_lep, decay_nu=decay_nu, output_name=prefix)
        with open(os.path.join(outdir, f"{prefix}_proc_card.dat"), "w") as f: f.write(proc)

        ## Generate customize, extramodels, and run_card
        with open(os.path.join(outdir, f"{prefix}_customizecards.dat"), "w") as f: 
            f.write(customize_template.format(mass=mass, isospin=isospin))
        with open(os.path.join(outdir, f"{prefix}_extramodels.dat"), "w") as f: 
            f.write(extramodels_template.format(model_archive=tarfile))
        with open(os.path.join(outdir, f"{prefix}_run_card.dat"), "w") as f: 
            f.write(run_card_template.format(beam_energy=proton_E))

        print(f"Done: \033[93m{outdir}\033[0m")
