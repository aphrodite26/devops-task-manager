
param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

$ImageRepository = "ghcr.io/aphrodite26/devops-task-manager"
$ComposeFile = Join-Path $PSScriptRoot "compose.yaml"
$OverrideFile = Join-Path $PSScriptRoot "deploy.override.yaml"

# Select the image to deploy
if ($Version -eq "rollback-test") {
    $TargetImage = "devops-task-manager:rollback-test"
    $IsLocalTest = $true
}
else {
    $TargetImage = "${ImageRepository}:${Version}"
    $IsLocalTest = $false
}

# Check application health
function Test-AppHealth {
    for ($i = 1; $i -le 15; $i++) {
        try {
            $response = Invoke-RestMethod `
                -Uri "http://localhost:5002/health" `
                -TimeoutSec 3

            if ($response.status -eq "healthy") {
                return $true
            }
        }
        catch {
            Write-Host "Health check attempt $i failed."
        }

        Start-Sleep -Seconds 2
    }

    return $false
}

# Save the currently deployed image
$containerId = docker compose -f $ComposeFile ps -q app

if ($LASTEXITCODE -ne 0) {
    throw "Failed to inspect the current deployment."
}

$previousImage = $null

if ($containerId) {
    $previousImage = docker inspect `
        --format '{{.Config.Image}}' `
        $containerId

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to inspect the previous image."
    }

    $previousImage = $previousImage.Trim()
}

Write-Host "Previous image: $previousImage"
Write-Host "Target image: $TargetImage"

# Prepare the new image
if ($IsLocalTest) {
    Write-Host "Checking local test image..."

    docker image inspect $TargetImage *> $null

    if ($LASTEXITCODE -ne 0) {
        throw "Local test image not found. Build it first."
    }
}
else {
    Write-Host "Pulling Docker image..."

    docker pull $TargetImage

    if ($LASTEXITCODE -ne 0) {
        throw "Image pull failed. Existing deployment unchanged."
    }
}

# Deploy the selected image
try {
    @"
services:
  app:
    image: "$TargetImage"
"@ | Set-Content -Path $OverrideFile

    Write-Host "Starting new application..."

    docker compose -f $ComposeFile -f $OverrideFile `
        up -d --no-deps --no-build --force-recreate app

    $deploymentStarted = ($LASTEXITCODE -eq 0)

    if ($deploymentStarted) {
        Write-Host "Checking application health..."

        if (Test-AppHealth) {
            Write-Host "Deployment completed successfully!"
            return
        }
    }

    Write-Host "Deployment failed. Starting rollback..."

    if (-not $previousImage) {
        throw "No previous image available for rollback."
    }

    # Restore the exact previous image
    @"
services:
  app:
    image: "$previousImage"
"@ | Set-Content -Path $OverrideFile

    Write-Host "Restoring previous image: $previousImage"

    docker compose -f $ComposeFile -f $OverrideFile `
        up -d --no-deps --no-build --force-recreate app

    if ($LASTEXITCODE -ne 0) {
        throw "Rollback failed: previous container could not start."
    }

    Write-Host "Checking rollback health..."

    if (-not (Test-AppHealth)) {
        throw "Rollback failed: previous application is unhealthy."
    }

    Write-Host "Rollback completed successfully!"
    throw "New deployment failed. Previous version restored."
}
finally {
    if (Test-Path $OverrideFile) {
        Remove-Item $OverrideFile -Force
    }
}
