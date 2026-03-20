#!/usr/bin/env python3
"""
plot_rutherford.py
------------------
Reads the Geant4 output file rutherford.root and plots:
  1. Simulated scattering angle distribution
  2. Comparison with the theoretical Rutherford formula:
       dσ/dΩ ∝ 1 / sin⁴(θ/2)

Usage:
    python3 plot_rutherford.py

Requires: uproot, numpy, matplotlib, scipy
Install:  pip3 install uproot awkward numpy matplotlib scipy
"""

import numpy as np
import matplotlib.pyplot as plt
import os

ROOT_FILE = "rutherford.root"

if not os.path.exists(ROOT_FILE):
    print(f"ERROR: {ROOT_FILE} not found.")
    print("Run the Geant4 simulation first: ./exampleB1 run_rutherford.mac")
    raise SystemExit(1)

try:
    import uproot
except ImportError:
    print("uproot not found. Installing...")
    import subprocess
    subprocess.check_call(["pip3", "install", "uproot", "awkward"])
    import uproot

# ── Read histogram from ROOT file ────────────────────────────────────────────
with uproot.open(ROOT_FILE) as f:
    print("Keys in ROOT file:", f.keys())
    # Geant4 Analysis Manager names histograms as h1_<name> or just the title
    # Try common key patterns
    hist = None
    for key in f.keys():
        if "theta" in key.lower() or "scatter" in key.lower() or "h1" in key.lower():
            hist = f[key]
            print(f"Using histogram: {key}")
            break
    if hist is None:
        # Just take the first histogram
        hist = f[f.keys()[0]]
        print(f"Using first histogram: {f.keys()[0]}")

    counts, edges = hist.to_numpy()
    centres = 0.5 * (edges[:-1] + edges[1:])

# ── Rutherford theoretical formula ───────────────────────────────────────────
# dσ/dΩ = (Z1*Z2*e²/4E)² * 1/sin⁴(θ/2)
# For relative comparison, just use 1/sin⁴(θ/2)
theta_theory = np.linspace(2, 178, 500)  # degrees, avoid 0 and 180
ruth_theory = 1.0 / np.sin(np.radians(theta_theory / 2))**4
ruth_theory /= ruth_theory.max()  # normalise to 1

# Normalise simulation counts
mask = counts > 0
counts_norm = counts / counts.max() if counts.max() > 0 else counts

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Rutherford Scattering — α (5 MeV) on Gold Foil\n(Geant4 Simulation)",
             fontsize=13, fontweight='bold')

# Left: raw counts
ax = axes[0]
ax.bar(centres, counts, width=(edges[1]-edges[0])*0.9,
       color='steelblue', alpha=0.75, label=f'Simulated  (N={int(counts.sum()):,})')
ax.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax.set_ylabel("Counts", fontsize=12)
ax.set_title("Simulated Scattering Angle Distribution", fontsize=11)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
ax.set_xlim(0, 180)

# Right: log scale comparison with Rutherford formula
ax2 = axes[1]
ax2.semilogy(centres[mask], counts_norm[mask], 'o',
             color='steelblue', markersize=4, label='Simulation (normalised)')
ax2.semilogy(theta_theory, ruth_theory, 'r-', linewidth=2,
             label=r'Rutherford: $1/\sin^4(\theta/2)$')
ax2.set_xlabel("Scattering Angle θ (degrees)", fontsize=12)
ax2.set_ylabel("Relative Cross Section (log scale)", fontsize=12)
ax2.set_title("Comparison with Rutherford Formula", fontsize=11)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, which='both')
ax2.set_xlim(0, 180)

plt.tight_layout()

os.makedirs("results", exist_ok=True)
plt.savefig("results/rutherford_scattering.png", dpi=150)
print("\nSaved: results/rutherford_scattering.png")
plt.show()

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\nTotal counts in histogram : {int(counts.sum()):,}")
print(f"Peak scattering angle     : {centres[counts.argmax()]:.1f}°")
print(f"Small angle dominance     : {counts[:18].sum()/counts.sum()*100:.1f}% of events < 18°")
