//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
/// \file B1/src/SteppingAction.cc
/// \brief Implementation of the B1::SteppingAction class

#include "SteppingAction.hh"
#include "G4AnalysisManager.hh"
#include "DetectorConstruction.hh"
#include "EventAction.hh"
#include "G4SystemOfUnits.hh"
#include "G4Event.hh"
#include "G4LogicalVolume.hh"
#include "G4RunManager.hh"
#include "G4Step.hh"

namespace B1
{

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SteppingAction::SteppingAction(const DetectorConstruction* detConstruction,
        EventAction* eventAction)
 : fDetConstruction(detConstruction) , fEventAction(eventAction) {}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SteppingAction::UserSteppingAction(const G4Step* step)
{
  auto scoringVolume =
    fDetConstruction->GetScoringVolume();

auto volume =
    step->GetPreStepPoint()
        ->GetTouchableHandle()
        ->GetVolume()
        ->GetLogicalVolume();

if (volume != scoringVolume) return;

// Only alpha
if (step->GetTrack()->GetDefinition()->GetParticleName() != "alpha")
    return;

// Count only when entering detector
if (step->GetPreStepPoint()->GetStepStatus() == fGeomBoundary)
{
    G4cout << "Alpha detected!" << G4endl;
}

// Gets direction of alpha, Extracts angle θ, Converts to degrees, Fills histogram

auto analysisManager = G4AnalysisManager::Instance();

G4ThreeVector dir = step->GetPostStepPoint()->GetMomentumDirection();
G4double theta = dir.theta() / deg;

analysisManager->FillH1(0, theta);

}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

}  // namespace B1
