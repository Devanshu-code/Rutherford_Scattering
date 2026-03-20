#include "RunAction.hh"
#include "DetectorConstruction.hh"
#include "PrimaryGeneratorAction.hh"
#include "G4AnalysisManager.hh"
#include "G4AccumulableManager.hh"
#include "G4LogicalVolume.hh"
#include "G4ParticleDefinition.hh"
#include "G4ParticleGun.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4UnitsTable.hh"

namespace B1
{

RunAction::RunAction()
{
  const G4double milligray = 1.e-3 * gray;
  const G4double microgray = 1.e-6 * gray;
  const G4double nanogray  = 1.e-9 * gray;
  const G4double picogray  = 1.e-12 * gray;
  new G4UnitDefinition("milligray", "milliGy", "Dose", milligray);
  new G4UnitDefinition("microgray", "microGy", "Dose", microgray);
  new G4UnitDefinition("nanogray",  "nanoGy",  "Dose", nanogray);
  new G4UnitDefinition("picogray",  "picoGy",  "Dose", picogray);

  G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
  accumulableManager->Register(fEdep);
  accumulableManager->Register(fEdep2);

  auto analysisManager = G4AnalysisManager::Instance();
  analysisManager->SetDefaultFileType("root");
  analysisManager->CreateH1("theta", "Scattering Angle", 180, 0., 180.);
}

void RunAction::BeginOfRunAction(const G4Run*)
{
  G4RunManager::GetRunManager()->SetRandomNumberStore(false);
  G4AccumulableManager::Instance()->Reset();

  auto analysisManager = G4AnalysisManager::Instance();
  // filename is set by /analysis/setFileName in the mac file
  analysisManager->OpenFile();
}

void RunAction::EndOfRunAction(const G4Run* run)
{
  G4int nofEvents = run->GetNumberOfEvent();
  if (nofEvents == 0) return;

  G4AccumulableManager::Instance()->Merge();

  G4double edep  = fEdep.GetValue();
  G4double edep2 = fEdep2.GetValue();
  G4double rms   = edep2 - edep * edep / nofEvents;
  rms = (rms > 0.) ? std::sqrt(rms) : 0.;

  const auto detConstruction = static_cast<const DetectorConstruction*>(
    G4RunManager::GetRunManager()->GetUserDetectorConstruction());
  G4double mass    = detConstruction->GetScoringVolume()->GetMass();
  G4double dose    = edep / mass;
  G4double rmsDose = rms / mass;

  auto analysisManager = G4AnalysisManager::Instance();
  analysisManager->Write();
  analysisManager->CloseFile();

  const auto generatorAction = static_cast<const PrimaryGeneratorAction*>(
    G4RunManager::GetRunManager()->GetUserPrimaryGeneratorAction());
  G4String runCondition;
  if (generatorAction) {
    const G4ParticleGun* gun = generatorAction->GetParticleGun();
    runCondition += gun->GetParticleDefinition()->GetParticleName();
    runCondition += " of ";
    runCondition += G4BestUnit(gun->GetParticleEnergy(), "Energy");
  }

  if (IsMaster())
    G4cout << G4endl << "--------------------End of Global Run-----------------------";
  else
    G4cout << G4endl << "--------------------End of Local Run------------------------";

  G4cout << G4endl << " The run: " << nofEvents << " " << runCondition << G4endl
         << " Dose in scoring volume: " << G4BestUnit(dose, "Dose")
         << " rms = " << G4BestUnit(rmsDose, "Dose") << G4endl
         << "------------------------------------------------------------" << G4endl;
}

void RunAction::AddEdep(G4double edep)
{
  fEdep  += edep;
  fEdep2 += edep * edep;
}

}  // namespace B1
