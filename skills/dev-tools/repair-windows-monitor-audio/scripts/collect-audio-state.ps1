[CmdletBinding()]
param(
    [switch]$PlayTestTone,
    [switch]$MeasureClock,
    [switch]$IncludeInactiveEndpoints,
    [string]$ReportPath
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'This collector requires Windows.' }
if (-not ('AudioProbe.Probe' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'CoreAudioProbe.cs') }
$endpoints = @([AudioProbe.Probe]::Snapshot())
$result = [ordered]@{
    collected_at = (Get-Date).ToUniversalTime().ToString('o')
    mode = 'ReadOnlySnapshot'
    endpoints = @($endpoints | Where-Object { $IncludeInactiveEndpoints -or $_.State -eq 1 })
    services = @(Get-Service -Name Audiosrv,AudioEndpointBuilder | Select-Object Name,@{n='Status';e={$_.Status.ToString()}},@{n='StartType';e={$_.StartType.ToString()}})
    devices = @(Get-PnpDevice -PresentOnly -Class Media,AudioEndpoint | Select-Object FriendlyName,Class,InstanceId,Status,Problem)
    audio_events = @()
    event_query_error = $null
    clock = $null
    tone = $null
    audibility = 'NotVerified'
}
try {
    $result.audio_events = @(Get-WinEvent -LogName 'Microsoft-Windows-Audio/Operational' -MaxEvents 25 -ErrorAction Stop | ForEach-Object {
        [xml]$xml = $_.ToXml()
        [pscustomobject]@{time=$_.TimeCreated.ToUniversalTime().ToString('o');id=$_.Id;message=$_.Message;data=$xml.Event.EventData.OuterXml}
    })
} catch { $result.event_query_error = $_.Exception.Message }
if ($MeasureClock) { $result.mode = 'SnapshotWithSilentStreamClock'; $result.clock = [AudioProbe.Probe]::MeasureClock() }
if ($PlayTestTone) {
    $console = @($endpoints | Where-Object { $_.Defaults -match 'Console' })
    $multimedia = @($endpoints | Where-Object { $_.Defaults -match 'Multimedia' })
    if ($console.Count -ne 1 -or $multimedia.Count -ne 1 -or $console[0].Id -ne $multimedia[0].Id) { throw 'Align Console and Multimedia default outputs before playing a test tone.' }
    $result.mode = 'SnapshotWithTestTone'
    $result.tone = [AudioProbe.Probe]::PlayAndMeasure()
}
$json = $result | ConvertTo-Json -Depth 8
if ($ReportPath) {
    $fullPath = [IO.Path]::GetFullPath($ReportPath)
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fullPath)) | Out-Null
    [IO.File]::WriteAllText($fullPath,$json,[Text.UTF8Encoding]::new($false))
}
$json
