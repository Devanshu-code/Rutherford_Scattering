#!/usr/bin/env python3
"""
plot_Estudy.py
--------------
Reads rutherford_4MeV.root, rutherford_8MeV.root, rutherford_12MeV.root
and plots scattering angle distributions for all energies on one figure.

Usage:
    python3 plot_Estudy.py

Requires: uproot, numpy, matplotlib
Install:  pip3 install uproot awkward numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import os, glob

try:
    import uproot
except ImportError:
    import subprocess
    subprocess.check_call(["pip3", "install", "uproot", "awkward"])
    import uproot

# Find all energy root files
root_files = sorted(glob.glob("rutherford_*MeV.root"))
if not root_files:
    # fallback: single file
    root_files = glob.glob("rutherford.root")

if not root_files:
    print("ERROR: No rutherford*.root files found.")
    print("Run: ./exampleB1 ../run_Estudy.mac")
    raise SystemExit(1)

print(f"Found files: {root_files}")

colors = ['royalblue', 'crimson', 'forestgreen', 'darkorange', 'purple']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(r"Rutherford Scattering — Energy Study ($\alpha$ on Gold Foil, Geant4)",
             fontsize=13, fontweight='bold')

ax_lin = axes[0]
ax_log = axes[1]

# Rutherford theoretical: 1/sin^4(theta/2)
theta_th = np.linspace(2, 178, 500)
ruth_th  = 1.0 / np.sin(np.radians(theta_th / 2))**4
ruth_th /= ruth_th.max()

for i, fpath in enumerate(root_files):
    # Extract energy label from filename
    label = os.path.basename(fpath).replace("rutherford_","").replace(".root","")

    with uproot.open(fpath) as f:
        key = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, edges = hist.to_numpy()

    centres = 0.5 * (edges[:-1] + edges[1:])
    col = colors[i % len(colors)]

    # Linear plot
    ax_lin.step(centres, counts, where='mid', color=col, linewidth=1.5,
                label=f"α {label}  (N={int(counts.sum()):,})")

    # Log plot — normalised
    mask = counts > 0
    norm = counts / counts.max()
    ax_log.semilogy(centres[mask], norm[mask], 'o', color=col,
                    markersize=3, label=f"α {label}")

# Add theoretical Rutherford curve
ax_log.semilogy(theta_th, ruth_th, 'k--', linewidth=1.5,
                label=r"Rutherford: $1/\sin^4(\theta/2)$")

ax_lin.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_lin.set_ylabel("Counts", fontsize=12)
ax_lin.set_title("Scattering Angle Distribution — All Energies", fontsize=11)
ax_lin.legend(fontsize=9); ax_lin.grid(True, alpha=0.3); ax_lin.set_xlim(0, 180)

ax_log.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_log.set_ylabel("Relative Cross Section (log scale)", fontsize=12)
ax_log.set_title("Comparison with Rutherford Formula", fontsize=11)
ax_log.legend(fontsize=9); ax_log.grid(True, alpha=0.3, which='both')
ax_log.set_xlim(0, 180)

plt.tight_layout()
os.makedirs("results", exist_ok=True)
plt.savefig("results/rutherford_Estudy.png", dpi=150)
print("Saved: results/rutherford_Estudy.png")
plt.show()

# Summary
print("\n" + "="*55)
print(f"  {'File':<30}  {'Total counts':>12}")
print("  " + "-"*45)
for fpath in root_files:
    with uproot.open(fpath) as f:
        key = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, _ = hist.to_numpy()
    print(f"  {os.path.basename(fpath):<30}  {int(counts.sum()):>12,}")
print("="*55)
