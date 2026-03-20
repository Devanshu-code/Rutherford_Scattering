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
/// \file B1/src/DetectorConstruction.cc
/// \brief Implementation of the B1::DetectorConstruction class

#include "DetectorConstruction.hh"

#include "G4Box.hh"
#include "G4Cons.hh"
#include "G4LogicalVolume.hh"
#include "G4NistManager.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4Trd.hh"
#include "G4Tubs.hh"

namespace B1
{

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4VPhysicalVolume* DetectorConstruction::Construct()
{
  // Get nist material manager
  G4NistManager* nist = G4NistManager::Instance();

  // Envelope parameters
  //
  G4double env_sizeXY = 10 * cm, env_sizeZ = 100 * cm;
  G4Material* env_mat = nist->FindOrBuildMaterial("G4_WATER");

  // Option to switch on/off checking of volumes overlaps
  //
  G4bool checkOverlaps = true;



  //
  // World
  //
  G4double world_sizeXY = 5 * env_sizeXY;
  G4double world_sizeZ = 5 * env_sizeZ;
  G4Material* world_mat = nist->FindOrBuildMaterial("G4_AIR");

  auto solidWorld =
    new G4Box("World",  // its name
              0.5 * world_sizeXY, 0.5 * world_sizeXY, 0.5 * world_sizeZ);  // its size

  auto logicWorld = new G4LogicalVolume(solidWorld,  // its solid
                                        world_mat,  // its material
                                        "World");  // its name

  auto physWorld = new G4PVPlacement(nullptr,  // no rotation
                                     G4ThreeVector(),  // at (0,0,0)
                                     logicWorld,  // its logical volume
                                     "World",  // its name
                                     nullptr,  // its mother  volume
                                     false,  // no boolean operation
                                     0,  // copy number
                                     checkOverlaps);  // overlaps checking

  

  // ===== Alpha Source =====
  G4Material* sourceMat = nist->FindOrBuildMaterial("G4_Al");

  G4double srcRadius = 5*mm;
  G4double srcThickness = 1*um;

  auto solidSrc = new G4Tubs("Source",
             0,
             srcRadius,
             srcThickness/2,
             0,
             360*deg);

  auto logicSrc = new G4LogicalVolume(solidSrc,
                      sourceMat,
                      "Source");


  new G4PVPlacement(nullptr,
                  G4ThreeVector(0,0,0),
                  logicSrc,
                  "Source",
                  logicWorld,
                  false,
                  0,
                  checkOverlaps);

  // ===== Foil =====
  G4Material* foilMat = nist->FindOrBuildMaterial("G4_Au");

  G4double foilRadius = 10*mm;
  G4double foilThickness = 5*um;  // adjustable

  auto solidFoil = new G4Tubs("Foil",
                            0,
                            foilRadius,
                            foilThickness/2,
                            0,
                            360*deg);

  auto logicFoil = new G4LogicalVolume(solidFoil,
                                     foilMat,
                                     "Foil");

  new G4PVPlacement(nullptr,
                  G4ThreeVector(0,0,2*mm),
                  logicFoil,
                  "Foil",
                  logicWorld,
                  false,
                  0,
                  checkOverlaps);
  // ===== Cylindrical Detector =====
  G4Material* detMat = nist->FindOrBuildMaterial("G4_Si");

  G4double detRadius = 15*mm;
  G4double detThickness = 6*mm;

  auto solidDet = new G4Tubs("Detector",
                           0,
                           detRadius,
                           detThickness/2,
                           0,
                           360*deg);

  auto logicDet = new G4LogicalVolume(solidDet,
                                    detMat,
                                    "Detector");

  // 🔥 VERY IMPORTANT LINE (Scoring Volume)
  fScoringVolume = logicDet;

  new G4PVPlacement(nullptr,
                  G4ThreeVector(0,0,10*mm),
                  logicDet,
                  "Detector",
                  logicWorld,
                  false,
                  0,
                  checkOverlaps);

  

 
                                         
                          
  //
  // always return the physical World
  //
 return physWorld;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

}  // namespace B1
