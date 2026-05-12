# -------------------------------------------------------------------------------------
# Script: generate_one_gridpack.py
# Purpose: Executes the gridpack_generation.sh script for a specific mass point.
#          Handles cleanup and moves the final tarball to EOS.
# Usage: python3 generate_one_gridpack.py --run Run3 --name VLLS_ele_M115
# -------------------------------------------------------------------------------------

import os
import subprocess
import argparse
import time
from datetime import timedelta

parser = argparse.ArgumentParser(description="Generate a single VLL gridpack.")
parser.add_argument('--name', required=True, help='Name of the gridpack (e.g. VLLS_ele_M115)')
parser.add_argument('--run', choices=['Run3', 'Run2UL'], required=True, help='Run era: Run3 or Run2UL')
parser.add_argument('--dryrun', action='store_true', help='Enable debug output (no execution)')
args = parser.parse_args()

## Configuration for each Run
config = {
    "Run3":   {"arch": "el8_amd64_gcc12",   "cmssw": "CMSSW_13_0_13"},
    "Run2UL": {"arch": "slc7_amd64_gcc700", "cmssw": "CMSSW_10_6_26"}
}

name = args.name
run = args.run
dryrun = args.dryrun
scram_arch = config[run]["arch"]
cmssw_version = config[run]["cmssw"]
queue = "local"

## Paths
basedir = os.getcwd()
mg5dir = os.path.join(basedir, run, "genproductions/bin/MadGraph5_aMCatNLO")
user = os.environ["USER"]
dumpdir = f"/eos/user/{user[0]}/{user}/VLLgridpacks_{run}"
if not dryrun: os.system(f"mkdir -p {dumpdir}")

#---------------------------------------------------------------------------------------------
## Cleanup logic
start_cleanup = time.time()
tempdir = os.path.join(dumpdir, "temp")
if not dryrun: os.makedirs(tempdir, exist_ok=True)

print(f"\033[93m\n==> Cleaning up the work directory. Moving previous log/tarballs to: {tempdir}\033[0m")
for entry in os.listdir(mg5dir):
    if entry.startswith("VLL"):
        path = os.path.join(mg5dir, entry)
        if os.path.isdir(path):
            command = f"rm -rf {path}"
            print(f">> \033[33;3m{command}\033[0m")
            if not dryrun: os.system(command)
        else:
            target = os.path.join(tempdir, entry)
            command = f"mv {path} {target}"
            command2 = f"mv {mg5dir}/*log {tempdir} 2>/dev/null" # added stderr redirect for cleaner logs
            print(f">> \033[33;3m{command}\033[0m")
            print(f">> \033[33;3m{command2}\033[0m")
            if not dryrun:
                os.system(command)
                os.system(command2)

end_cleanup = time.time()
cleanup_duration = timedelta(seconds=int(end_cleanup - start_cleanup))
print(f"Cleanup time taken: {str(cleanup_duration)}")

#---------------------------------------------------------------------------------------------
## Generation Execution
print(f"\033[93m\n==> Changing to: {mg5dir}\033[0m")
os.chdir(mg5dir)

start_gen = time.time()
print(f"\033[93m\n==> Running gridpack_generation.sh for {name}\033[0m")
carddir = os.path.join("cards", "VLL", name)

if not os.path.isdir(carddir):
    print(f"\033[31m!! Card directory not found: {carddir}\033[0m")
    exit(1)

command = f"./gridpack_generation.sh {name} {carddir} {queue} ALL {scram_arch} {cmssw_version}"
print(f">> \033[33;3m{command}\033[0m\n")

if dryrun:
    print("\033[93m[DRY RUN] Mode enabled: generation command skipped.\033[0m")
    exit(0)

# Main Execution
result = subprocess.run(command, shell=True)

end_gen = time.time()
gen_duration = timedelta(seconds=int(end_gen - start_gen))
print(f"Generation time taken: {str(gen_duration)}")

#---------------------------------------------------------------------------------------------
## Managing outputs
if result.returncode != 0:
    print("\033[31m!! Gridpack generation failed! Check the log files.\033[0m")
    exit(1)

print("\033[94m\n==> Gridpack generation complete.\033[0m")

tarball = f"{name}_{scram_arch}_{cmssw_version}_tarball.tar.xz"
source_tarball = os.path.join(mg5dir, tarball)
target_tarball = os.path.join(dumpdir, tarball)

print(f"\033[93m\n==> Moving gridpack to: {target_tarball}\033[0m")

if not os.path.exists(source_tarball):
    print(f"\033[31m!! Expected tarball not found: {source_tarball}\033[0m")
    exit(1)

try:
    subprocess.run(["cp", source_tarball, target_tarball], check=True)
    os.remove(source_tarball)
    print("\033[94m\n==> Gridpack successfully copied to EOS and removed from local disk.\033[0m\n")

except Exception as e:
    print(f"\033[31m!! Failed to move gridpack: {e}\033[0m")
    exit(1)
