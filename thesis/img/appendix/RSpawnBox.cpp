// Fill out your copyright notice in the Description page of Project Settings.

#include "RSpawnBox.h"
#include "RobCoG.h"
#include "Kismet/KismetMathLibrary.h"
#include "EngineUtils.h"
#include "TimerManager.h"
#include <string>

	// Log for this Class
	DEFINE_LOG_CATEGORY(SB_Log);

ASpawnBox::ASpawnBox()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

	// Sets up the components and initializes the SpawnVolume BoxExtent.
	RootComponent = CreateDefaultSubobject<USceneComponent>("Root");
	SpawnVolume = CreateDefaultSubobject<UBoxComponent>("SpawnBox");
	SpawnVolume->SetupAttachment(RootComponent);
	SpawnVolume->SetBoxExtent(FVector(40,40,10), true);
	SpawnVolume->bGenerateOverlapEvents = true;

	CameraRadius = 50;
  CameraHeight = 0;
  UpdateTime = 5.0f;
  Angle = 90.f;
  HeightAngle = 90.f;

  NoOfViewpoints = 3;
  NoOfHeightViewpoints = 2;
  HeightOffset = 20;
  bUseHeightViewPoints = false;
  bProcessHeightViewpoints = false;

  AngleAxis = 0.0f;

}

void ASpawnBox::BeginPlay()
{
	Super::BeginPlay();

  if(!ScanCamera)
  {
    UE_LOG(SB_Log, Log, TEXT("No Camera given. Please assign one!"));
  }


  // Angle to big, reset
  if(Angle >= 360)
  {
    Angle = 90.f;
    UE_LOG(SB_Log, Log, TEXT("This angle is too large. Please select between 0 and 360"));
  }

  if (bUseHeightViewPoints)
  {
    ProcessedViewpoints = NoOfViewpoints + NoOfHeightViewpoints;
  }
  else
  {
    ProcessedViewpoints = NoOfViewpoints;
    NoOfHeightViewpoints = 0;
  }

  SetUpCamera();
  GetWorldTimerManager().SetTimer(UpdateTimerHandle, this, &ASpawnBox::SetUpCamera, UpdateTime, true);
}

void ASpawnBox::Tick( float DeltaTime )
{
	Super::Tick( DeltaTime );
}

void ASpawnBox::SetUpCamera()
{
  if (ScanCamera)
  {
    if( ProcessedViewpoints == 0)
    {
      GetWorld()->GetTimerManager().ClearTimer(UpdateTimerHandle);
      bProcessHeightViewpoints = false;
      return;
    }


    float i;
    if (ProcessedViewpoints == NoOfViewpoints + NoOfHeightViewpoints)
    {
      i = NoOfViewpoints / 2;
      AngleAxis -= (HeightAngle * ((NoOfViewpoints % 2 != 0) ? i : (0.5 * i)));
    }
    else if (ProcessedViewpoints == NoOfHeightViewpoints)
    {
      AngleAxis = 0.0f;

      i = NoOfHeightViewpoints / 2;
      AngleAxis -= (HeightAngle * ((NoOfHeightViewpoints % 2 != 0) ? i : (0.5 * i)));
      bProcessHeightViewpoints = true;
    }
    else
    {
      // normal step
      // compute new location on a circle around the SpawnVolume
      AngleAxis += bProcessHeightViewpoints ? HeightAngle : Angle;
      if( AngleAxis >= 360.0f) { AngleAxis = 0; }
    }

    --ProcessedViewpoints;
    FVector NewLocation = SpawnVolume->GetComponentLocation();

    FVector RotateValue = FVector(CameraRadius, 0, 0).RotateAngleAxis(AngleAxis, FVector::UpVector);


    NewLocation.X += RotateValue.X;
    NewLocation.Y += RotateValue.Y;
    NewLocation.Z += bProcessHeightViewpoints ? (CameraHeight + HeightOffset) : CameraHeight;

    // the camera looks to the midpoint of the SpawnVolume
    FRotator Rot = UKismetMathLibrary::FindLookAtRotation(NewLocation, SpawnVolume->GetComponentLocation());

    ScanCamera->SetActorLocationAndRotation(NewLocation, Rot);
  }
}


void ASpawnBox::EndPlay(const EEndPlayReason::Type EndPlayReason)
{

}

