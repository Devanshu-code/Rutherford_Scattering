// exampleB1.cc — Rutherford Scattering Energy Study
// Varies alpha energy, records scattering angle distribution
// Output: rutherford.root → plot with Python

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
  G4UIExecutive* ui = nullptr;
  if (argc == 1) {
    ui = new G4UIExecutive(argc, argv);
  }

  G4Random::setTheEngine(new CLHEP::RanecuEngine);

  auto runManager =
    G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

  runManager->SetUserInitialization(new DetectorConstruction());
  runManager->SetUserInitialization(new QBBC);
  runManager->SetUserInitialization(new ActionInitialization());

  auto visManager = new G4VisExecutive;
  visManager->Initialize();

  auto UImanager = G4UImanager::GetUIpointer();

  if (!ui) {
    // Batch mode — no window
    UImanager->ApplyCommand(G4String("/control/execute ") + argv[1]);
  } else {
    // Interactive
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
