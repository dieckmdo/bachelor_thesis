// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "Object.h"
#include "GameFramework/Actor.h"
#include "Classes/Components/BoxComponent.h"
#include "Camera/CameraActor.h"
#include "URoboVision/Public/RGBDCamera.h"
#include "RSpawnBox.generated.h"

	// Log for this Class
	DECLARE_LOG_CATEGORY_EXTERN(SB_Log, Log, All);

UCLASS()
class ASpawnBox : public AActor
{
	GENERATED_BODY()
	
public:	
	/**
	 * Sets default values for this actor's properties
	 */
	ASpawnBox();

	/**
	 * Called when the game starts or when spawned
	 */
	virtual void BeginPlay() override;
	
	/** 
	 * Called every frame
	 */
	virtual void Tick( float DeltaSeconds ) override;

	/** The Volume in which the objects will be spawned*/
	UPROPERTY(EditAnywhere)
		UBoxComponent* SpawnVolume;

  /** The Camera used for scanning the scene */
  UPROPERTY(EditAnywhere, Category = "Camera Settings")
  ARGBDCamera* ScanCamera;

	/** The Radius, on which the Camera should rotate around the SpawnBox */
	UPROPERTY(EditAnywhere, Category = "Camera Settings")
		int CameraRadius;

	/** The Height of the Camera */
	UPROPERTY(EditAnywhere, Category = "Camera Settings")
		int CameraHeight;

  /** The angle the camera will be rotated around the SpawnVolume per rotation */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    float Angle;

  /** The time between the location updates of the camera */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    float UpdateTime;

  /** How much Viewpoints there are/how much locations the camera has */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    int NoOfViewpoints;

  /** The angle the camera will be rotated around for the viewpoints on the second height */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    float HeightAngle;

  /** Gets added to CameraHeight to describe the height for the second height rotations */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    int HeightOffset;

  /** The number of viewpoints on the second height rotations */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    int NoOfHeightViewpoints;

  /** True, if the ScanCamera should additionally scan on a second height */
  UPROPERTY(EditAnywhere, Category = "Scan Settings")
    bool bUseHeightViewPoints;

protected:
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;



private:

  /** Rotationangles for computing the ScanCamera location  */
  float AngleAxis;

  /** How many viewpoints have been processed */
  int ProcessedViewpoints;

  /** True, if all viewpoints on height 1 are processed */
  bool bProcessHeightViewpoints;

  /** Handle for updating the camera */
  FTimerHandle UpdateTimerHandle;

  /** Sets the location of the ScanCamera */
	void SetUpCamera();


};
