# #####################################################################################
# Script: move_cards.py
# Purpose: Moves the generated cards from the local dump directory to the 
#          MadGraph5_aMCatNLO/cards/VLL directory within the specific Run's genproductions.
# Usage: python3 move_cards.py --run Run3
# #####################################################################################

import os
import argparse

parser = argparse.ArgumentParser(description="Move cards to genproductions directory.")
parser.add_argument('--run', choices=['Run3', 'Run2UL'], required=True, help="Era: Run3 or Run2UL")
args = parser.parse_args()

run = args.run
source_dir = f"cards_{run}"
target_dir = os.path.join(run, "genproductions/bin/MadGraph5_aMCatNLO/cards/VLL")

if not os.path.isdir(source_dir):
    print(f"\033[91m[ERROR]\033[0m Source directory not found: {source_dir}")
    exit(1)

os.makedirs(target_dir, exist_ok=True)

for item in os.listdir(source_dir):
    src = os.path.join(source_dir, item)
    ## Using cp -r to avoid potential issues with moving across different filesystems
    command = f'cp -r {src} {target_dir}/'
    print(">> \033[33;3m" + command + "\033[0m")
    os.system(command)

print(f"\033[93m[DONE]\033[0m All cards from {source_dir} moved into {target_dir}")
