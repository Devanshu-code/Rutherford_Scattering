// exampleB1.cc — Rutherford Scattering Simulation
// Alpha particles (5 MeV) scattered off a gold foil
// Scattering angle histogram → rutherford.root → plot with Python

#include "ActionInitialization.hh"
#include "DetectorConstruction.hh"

#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "QBBC.hh"

#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"

#include "Randomize.hh"

using namespace B1;

int main(int argc, char** argv)
{
  // Detect batch vs interactive mode
  G4UIExecutive* ui = nullptr;
  if (argc == 1) {
    ui = new G4UIExecutive(argc, argv);
  }

  // Random engine
  G4Random::setTheEngine(new CLHEP::RanecuEngine);

  // Run manager
  auto runManager =
    G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

  // Geometry, physics, actions
  runManager->SetUserInitialization(new DetectorConstruction());
  runManager->SetUserInitialization(new QBBC);
  runManager->SetUserInitialization(new ActionInitialization());

  // Visualization
  auto visManager = new G4VisExecutive;
  visManager->Initialize();

  auto UImanager = G4UImanager::GetUIpointer();

  if (!ui) {
    // ── BATCH MODE ──────────────────────────────────────────────────────
    G4String command  = "/control/execute ";
    G4String fileName = argv[1];
    UImanager->ApplyCommand(command + fileName);
  } else {
    // ── INTERACTIVE MODE ─────────────────────────────────────────────────
    UImanager->ApplyCommand("/control/execute vis.mac");
    if (ui->IsGUI()) {
      UImanager->ApplyCommand("/control/execute gui.mac");
    }
    ui->SessionStart();
    delete ui;
  }

  delete visManager;
  delete runManager;
  return 0;
}
