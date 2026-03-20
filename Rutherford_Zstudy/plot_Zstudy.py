#!/usr/bin/env python3
"""
plot_Zstudy.py
--------------
Reads rutherford_Al_Z13.root, rutherford_Cu_Z29.root, rutherford_Au_Z79.root
and plots scattering angle distributions for different foil materials (Z study).

Physics: Higher Z → stronger Coulomb force → more large-angle scattering
         dσ/dΩ ∝ Z² / sin⁴(θ/2)

Usage:
    python3 plot_Zstudy.py

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

root_files = sorted(glob.glob("rutherford_*_Z*.root"))
if not root_files:
    print("ERROR: No rutherford_*_Z*.root files found.")
    print("Run: ./exampleB1 ../run_Al.mac  etc.")
    raise SystemExit(1)

print(f"Found: {root_files}")

# Z values for Rutherford scaling
Z_map = {"Al": 13, "Cu": 29, "Au": 79}
colors = {'Al': 'royalblue', 'Cu': 'crimson', 'Au': 'forestgreen'}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(r"Rutherford Scattering — Atomic Number (Z) Study"
             "\n" r"($\alpha$ 5 MeV, Foil 5 μm, Geant4)",
             fontsize=13, fontweight='bold')

ax_lin = axes[0]
ax_log = axes[1]

# Theoretical Rutherford: dσ/dΩ ∝ Z² / sin⁴(θ/2)
theta_th = np.linspace(2, 178, 500)
sin4     = np.sin(np.radians(theta_th / 2))**4

for fpath in root_files:
    fname = os.path.basename(fpath).replace(".root", "")
    # Extract material name: rutherford_Al_Z13 → Al
    mat_match = re.search(r'rutherford_(\w+)_Z\d+', fname)
    mat   = mat_match.group(1) if mat_match else fname
    Z     = Z_map.get(mat, 1)
    col   = colors.get(mat, 'purple')
    label = f"{mat} (Z={Z})"

    with uproot.open(fpath) as f:
        key  = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, edges = hist.to_numpy()

    centres = 0.5 * (edges[:-1] + edges[1:])

    ax_lin.step(centres, counts, where='mid', color=col, linewidth=1.5,
                label=f"{label}  (N={int(counts.sum()):,})")

    mask = counts > 0
    norm = counts / counts.max()
    ax_log.semilogy(centres[mask], norm[mask], 'o', color=col,
                    markersize=3, label=f"{label} data")

    # Rutherford theory scaled by Z²
    ruth = Z**2 / sin4
    ruth /= ruth.max()
    ax_log.semilogy(theta_th, ruth, '--', color=col, linewidth=1.2, alpha=0.6,
                    label=f"Rutherford Z²={Z**2}")

ax_lin.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_lin.set_ylabel("Counts", fontsize=12)
ax_lin.set_title("Scattering Angle — All Materials", fontsize=11)
ax_lin.legend(fontsize=9); ax_lin.grid(True, alpha=0.3); ax_lin.set_xlim(0, 180)

ax_log.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax_log.set_ylabel("Relative Cross Section (log scale)", fontsize=12)
ax_log.set_title(r"Comparison with Rutherford: $d\sigma/d\Omega \propto Z^2/\sin^4(\theta/2)$",
                 fontsize=11)
ax_log.legend(fontsize=8); ax_log.grid(True, alpha=0.3, which='both')
ax_log.set_xlim(0, 180)

plt.tight_layout()
os.makedirs("results", exist_ok=True)
plt.savefig("results/rutherford_Zstudy.png", dpi=150)
print("Saved: results/rutherford_Zstudy.png")
plt.show()

print("\n" + "="*55)
print(f"  {'Material':<12} {'Z':>4} {'Z²':>6} {'Total counts':>12}")
print("  " + "-"*40)
for fpath in sorted(root_files):
    fname = os.path.basename(fpath).replace(".root","")
    mat_match = re.search(r'rutherford_(\w+)_Z(\d+)', fname)
    mat = mat_match.group(1) if mat_match else fname
    Z   = int(mat_match.group(2)) if mat_match else 0
    with uproot.open(fpath) as f:
        key = [k for k in f.keys() if "theta" in k.lower() or "h1" in k.lower()]
        hist = f[key[0]] if key else f[f.keys()[0]]
        counts, _ = hist.to_numpy()
    print(f"  {mat:<12} {Z:>4} {Z**2:>6} {int(counts.sum()):>12,}")
print("="*55)
