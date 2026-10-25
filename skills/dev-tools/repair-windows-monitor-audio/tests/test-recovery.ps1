# All OS/device mutations in this file are isolated fixtures, never real repairs.
$ErrorActionPreference = 'Stop'
if (-not ('System.ServiceProcess.ServiceControllerStatus' -as [type])) { Add-Type -AssemblyName System.ServiceProcess }
$script:audioId = 'HDAUDIO\FUNC_01&VEN_10DE&DEV_TEST\MOCK'
$script:controllerId = 'PCI\VEN_10DE&DEV_TEST\AUDIO'
function Reset-Fixture {
    $script:fixture = @{ambiguous=$false;parentClass='System';parentVendor='10DE';pending=$false;admin=$true;held=$false;nativeCode=0;nativeThrows=$false;stopThrows=$false;startFails='';targetChanges=$false;stops=0;nativeCalls=0;nativeTarget='';starts=@();states=@{Audiosrv='Running';RtkMock='Running';ChildMock='Running'}}
}
function Get-PnpDevice {
    param([string]$InstanceId,[string]$Class,[switch]$PresentOnly)
    if (-not $InstanceId) {
        $entry = [pscustomobject]@{FriendlyName='NVIDIA High Definition Audio';Class='MEDIA';InstanceId=$script:audioId;Status='OK';Problem=0}
        $entry
        if ($script:fixture.ambiguous) { [pscustomobject]@{FriendlyName='NVIDIA High Definition Audio';Class='MEDIA';InstanceId=($script:audioId+'2');Status='OK';Problem=0} }
    } elseif ($InstanceId -match '^PCI') {
        [pscustomobject]@{FriendlyName='Fixture Audio Controller';Class=$script:fixture.parentClass;InstanceId=$InstanceId;Status='OK';Problem=0}
    } else {
        [pscustomobject]@{FriendlyName='Fixture Audio Codec';Class='MEDIA';InstanceId=$InstanceId;Status='OK';Problem=0}
    }
}
function Get-PnpDeviceProperty {
    param([string]$InstanceId,[string]$KeyName)
    switch ($KeyName) {
        'DEVPKEY_Device_Parent' {
            $id = $script:controllerId -replace 'VEN_10DE',('VEN_'+$script:fixture.parentVendor)
            if ($script:fixture.targetChanges -and $script:fixture.states.Audiosrv -eq 'Stopped') { $id += 'CHANGED' }
            [pscustomobject]@{Data=$id}
        }
        'DEVPKEY_Device_Service' { [pscustomobject]@{Data='HDAudBus'} }
        'DEVPKEY_Device_IsRebootRequired' { [pscustomobject]@{Data=([bool]$script:fixture.pending)} }
        default { throw 'Unexpected property requested by fixture.' }
    }
}
function Get-Service {
    param([string[]]$Name)
    foreach ($item in $Name) {
        $deps = @()
        if ($item -eq 'Audiosrv') { $deps = @([pscustomobject]@{Name='RtkMock';Status=$script:fixture.states.RtkMock}) }
        if ($item -eq 'RtkMock') { $deps = @([pscustomobject]@{Name='ChildMock';Status=$script:fixture.states.ChildMock}) }
        $service = [pscustomobject]@{Name=$item;Status=$script:fixture.states[$item];StartType='Automatic';DependentServices=$deps}
        $service | Add-Member -MemberType ScriptMethod -Name WaitForStatus -Value { param($status,$timeout) if ($this.Status -ne $status.ToString()) { throw 'Fixture service failed to reach expected state.' } }
        $service
    }
}
function Stop-Service {
    param([string]$Name,[switch]$Force)
    $script:fixture.stops++
    foreach ($item in @('Audiosrv','RtkMock','ChildMock')) { $script:fixture.states[$item]='Stopped' }
    if ($script:fixture.stopThrows) { throw 'Fixture Stop-Service failure after dependent shutdown.' }
}
function Start-Service {
    param([string]$Name)
    $script:fixture.starts += $Name
    if ($Name -eq $script:fixture.startFails) { throw 'Fixture service restoration failure.' }
    $script:fixture.states[$Name]='Running'
}
function Get-Process { param([string]$Name) if ($script:fixture.held) { [pscustomobject]@{Name='audiodg';Id=1} } }
function Start-Sleep { param([int]$Milliseconds) }
Reset-Fixture
$recoveryPath = Join-Path $PSScriptRoot '../scripts/restart-nvidia-audio-controller.ps1'
$null = . $recoveryPath
function Test-AudioRepairAdministrator { $script:fixture.admin }
function Invoke-AudioRepairNativeRestart {
    param([string]$ControllerInstanceId)
    $script:fixture.nativeCalls++
    $script:fixture.nativeTarget=$ControllerInstanceId
    if ($script:fixture.nativeThrows) { throw 'Fixture native invocation failed.' }
    [pscustomobject]@{exit_code=$script:fixture.nativeCode;output='Fixture PnP result'}
}
function Assert-That { param([bool]$Condition,[string]$Message) if (-not $Condition) { throw $Message } }
function Assert-Restored { foreach ($name in @('Audiosrv','RtkMock','ChildMock')) { Assert-That ($script:fixture.states[$name] -eq 'Running') ('Service not restored: '+$name) } }
function Expect-Error { param([scriptblock]$Action) $failed=$false;try { & $Action | Out-Null } catch { $failed=$true };Assert-That $failed 'Expected an error, but the repair returned success.' }
$script:passed = 0
function Test-Case { param([string]$Name,[scriptblock]$Body) Reset-Fixture;try { & $Body } catch { Write-Output ('FAIL '+$Name); $Error | Select-Object -First 3 | ForEach-Object { Write-Output $_.Exception.Message }; throw };$script:passed++;Write-Output ('PASS '+$Name) }
Test-Case 'default preflight is read only' {
    $result = Invoke-AudioControllerRepair | ConvertFrom-Json
    Assert-That ($result.status -eq 'PreflightOnly') 'Wrong preflight status.'
    Assert-That ($script:fixture.stops -eq 0 -and $script:fixture.nativeCalls -eq 0) 'Preflight mutated audio.'
}
Test-Case 'Apply WhatIf does not require admin or mutate' {
    $script:fixture.admin=$false
    $result = Invoke-AudioControllerRepair -Apply -WhatIf | ConvertFrom-Json
    Assert-That ($result.status -eq 'PreflightOnly' -and $script:fixture.stops -eq 0) 'WhatIf applied a repair.'
}
Test-Case 'ambiguous audio selection is rejected' {
    $script:fixture.ambiguous=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.stops -eq 0) 'Ambiguous selection stopped services.'
}
Test-Case 'explicit audio selection resolves ambiguity without repair' {
    $script:fixture.ambiguous=$true
    $result=Invoke-AudioControllerRepair -AudioDeviceInstanceId $script:audioId | ConvertFrom-Json
    Assert-That ($result.target.Audio.InstanceId -eq $script:audioId -and $script:fixture.nativeCalls -eq 0) 'Explicit selection failed.'
}
Test-Case 'Display parent is rejected' {
    $script:fixture.parentClass='Display'
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.stops -eq 0) 'Display parent caused a mutation.'
}
Test-Case 'non NVIDIA parent is rejected' {
    $script:fixture.parentVendor='1002'
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.stops -eq 0) 'Wrong vendor caused a mutation.'
}
Test-Case 'controller pending reboot is rejected before stop' {
    $script:fixture.pending=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.stops -eq 0) 'Pending reboot controller was stopped.'
}
Test-Case 'unelevated Apply is rejected before stop' {
    $script:fixture.admin=$false
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.stops -eq 0) 'Unelevated repair stopped audio.'
}
Test-Case 'success restarts only the verified controller and restores transitive dependents' {
    $result=Invoke-AudioControllerRepair -Apply | ConvertFrom-Json
    Assert-That ($result.status -eq 'ControllerRestarted') 'Successful native call was not recorded.'
    Assert-That ($script:fixture.nativeCalls -eq 1 -and $script:fixture.nativeTarget -eq $script:controllerId) 'Wrong reset target or repeat.'
    Assert-That ($result.audibility -eq 'NotVerified') 'Script claimed the user heard sound.'
    Assert-Restored
}
foreach ($nativeCode in @(3010,50)) {
    Test-Case ('native '+$nativeCode+' is failure, restores services and does not retry') {
        $script:fixture.nativeCode=$nativeCode
        Expect-Error { Invoke-AudioControllerRepair -Apply }
        Assert-That ($script:fixture.nativeCalls -eq 1) 'Native failure caused another reset.'
        Assert-Restored
    }
}
Test-Case 'held audiodg causes restore without device reset' {
    $script:fixture.held=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.nativeCalls -eq 0) 'Held engine was ignored.'
    Assert-Restored
}
Test-Case 'native exception restores all prior running services' {
    $script:fixture.nativeThrows=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-Restored
}
Test-Case 'partial service stop failure still restores dependents' {
    $script:fixture.stopThrows=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.nativeCalls -eq 0) 'Stop failure caused device reset.'
    Assert-Restored
}
Test-Case 'restore failure is reported and does not skip later services' {
    $script:fixture.startFails='RtkMock'
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.starts -contains 'ChildMock') 'Restoration stopped after one failure.'
    Assert-That ($script:fixture.states.RtkMock -eq 'Stopped') 'The restore failure was hidden.'
}
Test-Case 'changed parent during stopped service is rejected' {
    $script:fixture.targetChanges=$true
    Expect-Error { Invoke-AudioControllerRepair -Apply }
    Assert-That ($script:fixture.nativeCalls -eq 0) 'Target change was ignored.'
    Assert-Restored
}
Write-Output ('Passed {0} isolated recovery checks; no real service or device was modified.' -f $script:passed)
