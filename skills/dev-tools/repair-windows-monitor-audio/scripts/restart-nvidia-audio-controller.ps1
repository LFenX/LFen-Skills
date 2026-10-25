[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [string]$AudioDeviceInstanceId,
    [switch]$Apply,
    [string]$ReportPath
)

function Get-AudioRepairTarget {
    param([string]$InstanceId)
    if ($InstanceId) {
        $audio = Get-PnpDevice -InstanceId $InstanceId -ErrorAction Stop
    } else {
        $candidates = @(Get-PnpDevice -PresentOnly -Class Media -ErrorAction Stop | Where-Object { $_.InstanceId -match '^HDAUDIO\\FUNC_01&VEN_10DE&' })
        if ($candidates.Count -ne 1) { throw ('Expected one NVIDIA audio codec; found {0}. Select its exact HDAUDIO InstanceId explicitly.' -f $candidates.Count) }
        $audio = $candidates[0]
    }
    if ($audio.Class -ne 'MEDIA' -or $audio.InstanceId -notmatch '^HDAUDIO\\FUNC_01&VEN_10DE&') { throw 'Selected device is not a NVIDIA HDAUDIO media device.' }
    $parentId = (Get-PnpDeviceProperty -InstanceId $audio.InstanceId -KeyName DEVPKEY_Device_Parent -ErrorAction Stop).Data
    if (-not $parentId) { throw 'The audio device has no verified immediate parent.' }
    $controller = Get-PnpDevice -InstanceId $parentId -ErrorAction Stop
    $service = (Get-PnpDeviceProperty -InstanceId $controller.InstanceId -KeyName DEVPKEY_Device_Service -ErrorAction Stop).Data
    if ($controller.Class -ne 'System' -or $service -ne 'HDAudBus' -or $controller.InstanceId -notmatch '^PCI\\VEN_10DE&') { throw 'Parent is not a verified NVIDIA audio-only System/HDAudBus controller. No reset is allowed.' }
    $pending = (Get-PnpDeviceProperty -InstanceId $controller.InstanceId -KeyName DEVPKEY_Device_IsRebootRequired -ErrorAction Stop).Data
    [pscustomobject]@{
        Audio = $audio | Select-Object FriendlyName,Class,InstanceId,Status,Problem
        Controller = $controller | Select-Object FriendlyName,Class,InstanceId,Status,Problem
        ControllerService = $service
        ControllerRebootRequired = [bool]$pending
    }
}

function Test-AudioRepairAdministrator {
    $principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
    $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-AudioRepairRunningDependents {
    $pending = [Collections.Generic.Queue[string]]::new()
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $pending.Enqueue('Audiosrv')
    while ($pending.Count -gt 0) {
        $serviceName = $pending.Dequeue()
        foreach ($dependent in (Get-Service -Name $serviceName -ErrorAction Stop).DependentServices) {
            if ($dependent.Status -eq 'Running' -and $seen.Add($dependent.Name)) {
                $dependent.Name
                $pending.Enqueue($dependent.Name)
            }
        }
    }
}

function Invoke-AudioRepairNativeRestart {
    param([string]$ControllerInstanceId)
    $output = (& "$env:WINDIR\System32\pnputil.exe" /restart-device $ControllerInstanceId 2>&1 | Out-String)
    [pscustomobject]@{exit_code=$LASTEXITCODE;output=$output}
}

function Invoke-AudioControllerRepair {
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
    param([string]$AudioDeviceInstanceId,[switch]$Apply,[string]$ReportPath)
    $ErrorActionPreference = 'Stop'
    if ($env:OS -ne 'Windows_NT') { throw 'This recovery requires Windows.' }
    $target = Get-AudioRepairTarget -InstanceId $AudioDeviceInstanceId
    $result = [ordered]@{
        started_at = (Get-Date).ToUniversalTime().ToString('o')
        status = 'PreflightOnly'
        target = $target
        services_before = @()
        services_after = @()
        native_result = $null
        devices_after = @()
        error = $null
        restore_errors = @()
        audibility = 'NotVerified'
    }
    $shouldApply = $Apply -and $PSCmdlet.ShouldProcess($target.Controller.InstanceId,'Stop Windows Audio, restart verified audio-only controller once, restore services')
    if ($shouldApply) {
        if (-not (Test-AudioRepairAdministrator)) { throw 'Run this script in an Administrator PowerShell after authorizing the exact target. No change was made.' }
        if ($target.ControllerRebootRequired) { throw 'The audio controller already requires a system restart. No change was made.' }
        if ((Get-Service -Name Audiosrv).Status -ne 'Running') { throw 'Windows Audio is not Running. Diagnose the service before attempting a controller recovery.' }
        $runningDependents = @(Get-AudioRepairRunningDependents)
        $serviceNames = @('Audiosrv') + $runningDependents
        $result.services_before = @(Get-Service -Name $serviceNames | Select-Object Name,@{n='Status';e={$_.Status.ToString()}},@{n='StartType';e={$_.StartType.ToString()}})
        $restoreAudio = $false
        try {
            $restoreAudio = $true
            Stop-Service -Name Audiosrv -Force -ErrorAction Stop
            (Get-Service -Name Audiosrv).WaitForStatus([System.ServiceProcess.ServiceControllerStatus]::Stopped,[TimeSpan]::FromSeconds(20))
            for ($attempt = 0; $attempt -lt 20; $attempt++) {
                if (-not (Get-Process -Name audiodg -ErrorAction SilentlyContinue)) { break }
                Start-Sleep -Milliseconds 250
            }
            if (Get-Process -Name audiodg -ErrorAction SilentlyContinue) { throw 'audiodg still holds the audio path. Restoring services without a device restart.' }
            $current = Get-AudioRepairTarget -InstanceId $target.Audio.InstanceId
            if ($current.Controller.InstanceId -ne $target.Controller.InstanceId -or $current.ControllerRebootRequired) { throw 'The controller identity or restart requirement changed. No device reset was attempted.' }
            $result.native_result = Invoke-AudioRepairNativeRestart -ControllerInstanceId $target.Controller.InstanceId
            if ($result.native_result.exit_code -ne 0) { throw ('PnPUtil returned {0}; stop here without rebooting or retrying.' -f $result.native_result.exit_code) }
            $result.status = 'ControllerRestarted'
        } catch {
            $result.status = 'RecoveryFailed'
            $result.error = $_.Exception.Message
        } finally {
            if ($restoreAudio) {
                try { Start-Service -Name Audiosrv -ErrorAction Stop } catch { $result.restore_errors += ('Audiosrv: ' + $_.Exception.Message) }
            }
            foreach ($dependentName in $runningDependents) {
                try { Start-Service -Name $dependentName -ErrorAction Stop } catch { $result.restore_errors += ($dependentName + ': ' + $_.Exception.Message) }
            }
            foreach ($serviceName in $serviceNames) {
                try {
                    $service = Get-Service -Name $serviceName -ErrorAction Stop
                    $result.services_after += $service | Select-Object Name,@{n='Status';e={$_.Status.ToString()}},@{n='StartType';e={$_.StartType.ToString()}}
                    if ($service.Status -ne 'Running') { $result.restore_errors += ($serviceName + ' is not Running after restoration.') }
                } catch { $result.restore_errors += ($serviceName + ': ' + $_.Exception.Message) }
            }
            foreach ($deviceId in @($target.Controller.InstanceId,$target.Audio.InstanceId)) {
                try {
                    $device = Get-PnpDevice -InstanceId $deviceId -ErrorAction Stop
                    $reboot = (Get-PnpDeviceProperty -InstanceId $deviceId -KeyName DEVPKEY_Device_IsRebootRequired -ErrorAction Stop).Data
                    $result.devices_after += [pscustomobject]@{name=$device.FriendlyName;instance_id=$device.InstanceId;status=$device.Status;problem=$device.Problem;reboot_required=[bool]$reboot}
                    if ($device.Status -ne 'OK' -or $reboot) { $result.restore_errors += ('Device requires follow-up: ' + $device.FriendlyName) }
                } catch { $result.restore_errors += $_.Exception.Message }
            }
            if ($result.restore_errors.Count -gt 0) { $result.status = 'RecoveryNeedsAttention' }
        }
    }
    $result.completed_at = (Get-Date).ToUniversalTime().ToString('o')
    $json = $result | ConvertTo-Json -Depth 9
    if ($ReportPath) {
        $fullPath = [IO.Path]::GetFullPath($ReportPath)
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fullPath)) | Out-Null
        [IO.File]::WriteAllText($fullPath,$json,[Text.UTF8Encoding]::new($false))
    }
    $json
    if ($result.status -in @('RecoveryFailed','RecoveryNeedsAttention')) { throw ('Recovery did not finish cleanly; inspect the JSON report. Status: ' + $result.status) }
}

Invoke-AudioControllerRepair @PSBoundParameters
