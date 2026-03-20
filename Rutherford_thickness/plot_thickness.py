#!/usr/bin/env python3
"""
plot_thickness.py
-----------------
Reads rutherford_1um.root, rutherford_5um.root, rutherford_10um.root
and plots scattering angle distributions for all foil thicknesses.

Usage:
    python3 plot_thickness.py

Requires: uproot, numpy, matplotlib
Install:  pip3 install uproot awkward numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import os, glob, re

try:
    import uproot
except ImportError:
    import subprocess
    subprocess.check_call(["pip3", "install", "uproot", "awkward"])
    import uproot

root_files = sorted(glob.glob("rutherford_*um.root"))
if not root_files:
    print("ERROR: No rutherford_*um.root files found.")
    print("Run: ./exampleB1 ../run_1um.mac  etc.")
    raise SystemExit(1)

print(f"Found: {root_files}")

colors = ['royalblue', 'crimson', 'forestgreen', 'darkorange']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(r"Rutherford Scattering — Foil Thickness Study ($\alpha$ 5 MeV on Gold, Geant4)",
             fontsize=13, fontweight='bold')

ax_lin = axes[0]
ax_log = axes[1]

# Theoretical Rutherford
theta_th = np.linspace(2, 178, 500)
ruth_th  = 1.0 / np.sin(np.radians(theta_th / 2))**4
ruth_th /= ruth_th.max()

for i, fpath in enumerate(root_files):
    label = os.path.basename(fpath).replace("rutherford_","").replace(".root","")
    col   = colors[i % len(colors)]

    with uproot.open(fpath) as f:
        key  = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, edges = hist.to_numpy()

    centres = 0.5 * (edges[:-1] + edges[1:])

    ax_lin.step(centres, counts, where='mid', color=col, linewidth=1.5,
                label=f"Au foil {label}  (N={int(counts.sum()):,})")

    mask = counts > 0
    norm = counts / counts.max()
    ax_log.semilogy(centres[mask], norm[mask], 'o', color=col,
                    markersize=3, label=f"Au foil {label}")

ax_log.semilogy(theta_th, ruth_th, 'k--', linewidth=1.5,
                label=r"Rutherford: $1/\sin^4(\theta/2)$")

ax_lin.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_lin.set_ylabel("Counts", fontsize=12)
ax_lin.set_title("Scattering Angle — All Foil Thicknesses", fontsize=11)
ax_lin.legend(fontsize=9); ax_lin.grid(True, alpha=0.3); ax_lin.set_xlim(0, 180)

ax_log.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_log.set_ylabel("Relative Cross Section (log scale)", fontsize=12)
ax_log.set_title("Comparison with Rutherford Formula", fontsize=11)
ax_log.legend(fontsize=9); ax_log.grid(True, alpha=0.3, which='both')
ax_log.set_xlim(0, 180)

plt.tight_layout()
os.makedirs("results", exist_ok=True)
plt.savefig("results/rutherford_thickness.png", dpi=150)
print("Saved: results/rutherford_thickness.png")
plt.show()

print("\n" + "="*50)
print(f"  {'Thickness':<15}  {'Total counts':>12}")
print("  " + "-"*35)
for fpath in root_files:
    with uproot.open(fpath) as f:
        key = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, _ = hist.to_numpy()
    label = os.path.basename(fpath).replace("rutherford_","").replace(".root","")
    print(f"  {label:<15}  {int(counts.sum()):>12,}")
print("="*50)
