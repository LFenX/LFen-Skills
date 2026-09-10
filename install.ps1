# LFen Skills - Terminal UI Installer
# Online:  iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
# Local:   .\install.ps1
# Silent:  .\install.ps1 -All -AllSkills -Force

param(
    [switch]$All, [switch]$AllSkills, [switch]$Force,
    [switch]$OpenCode, [switch]$Claude, [switch]$Codex,
    [switch]$Cursor, [switch]$Gemini, [switch]$Copilot, [switch]$Windsurf,
    [string]$Skills = "",
    [switch]$Update, [switch]$Status
)

$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/LFenX/LFen-Skills.git"
$repoDir = "$env:USERPROFILE\.lfenskills"
$skillsRoot = "$repoDir\skills"
$versionFile = "$env:USERPROFILE\.lfenskills-version"
$host.UI.RawUI.CursorSize = 0

# ANSI escape codes
$ansi = @{
    reset = "$([char]27)[0m"
    bold  = "$([char]27)[1m"
    dim   = "$([char]27)[2m"
    cyan  = "$([char]27)[36m"
    green = "$([char]27)[32m"
    yellow= "$([char]27)[33m"
    red   = "$([char]27)[31m"
    magenta="$([char]27)[35m"
    gray  = "$([char]27)[90m"
    white = "$([char]27)[37m"
}
function ac($c, $t) { "$($ansi[$c])$t$($ansi.reset)" }

function banner($mode) {
    Clear-Host
    Write-Host ""
    Write-Host (ac cyan "  ██╗     ███████╗███████╗███╗   ██╗")
    Write-Host (ac cyan "  ██║     ██╔════╝██╔════╝████╗  ██║")
    Write-Host (ac cyan "  ██║     █████╗  █████╗  ██╔██╗ ██║")
    Write-Host (ac cyan "  ██║     ██╔══╝  ██╔══╝  ██║╚██╗██║")
    Write-Host (ac cyan "  ███████╗██║     ███████╗██║ ╚████║")
    Write-Host (ac cyan "  ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝")
    Write-Host (ac yellow "  Skills $mode")
    Write-Host ""
}

# ─── Platforms ───
$platforms = @(
    @{key="opencode"; label="OpenCode";           dir="$env:USERPROFILE\.agents\skills";          note="also covers Cline/Warp/Zed/Kilo +17 more"}
    @{key="claude";   label="Claude Code";        dir="$env:USERPROFILE\.claude\skills";           note=""}
    @{key="codex";    label="Codex";              dir="$env:USERPROFILE\.codex\skills";            note=""}
    @{key="cursor";   label="Cursor";             dir="$env:USERPROFILE\.cursor\skills";           note=""}
    @{key="gemini";   label="Gemini CLI";         dir="$env:USERPROFILE\.gemini\skills";           note=""}
    @{key="copilot";  label="GitHub Copilot";     dir="$env:USERPROFILE\.copilot\skills";          note=""}
    @{key="windsurf"; label="Windsurf";           dir="$env:USERPROFILE\.codeium\windsurf\skills"; note=""}
)

# ─── Arrow-key menu engine ───
function Show-Menu($title, $items, $multi, $checkedList) {
    $selected = 0; $total = $items.Count

    while ($true) {
        $startLine = [Console]::CursorTop
        if ($title) { Write-Host (ac yellow "  $title") }

        for ($i = 0; $i -lt $total; $i++) {
            $cursor = if ($i -eq $selected) { (ac cyan "  ›") } else { "   " }
            $name = if ($i -eq $selected) { (ac cyan $items[$i].label) } else { $items[$i].label }

            $chk = ""
            if ($multi) {
                $chk = if ($checkedList[$i]) { (ac cyan "[✓] ") } else { "[ ] " }
            }

            $extra = @()
            if ($items[$i].extra) { $extra += $items[$i].extra }
            if ($items[$i].note) { $extra += (ac gray "($($items[$i].note))") }
            if ($items[$i].status) { $extra += $items[$i].status }

            $line = "$cursor $chk$name"
            if ($extra.Count -gt 0) { $line += "  " + ($extra -join "  ") }
            Write-Host $line
        }

        if ($multi) {
            Write-Host (ac gray "`n  [↑↓] Navigate  [Space] Toggle  [a] Select All  [Enter] Confirm  [q] Quit")
        } else {
            Write-Host (ac gray "`n  [↑↓] Navigate  [Enter] Select  [q] Quit")
        }

        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode

        # clear previously rendered block
        $linesToClear = (($total + 3) * 2)
        for ($j = 0; $j -lt $linesToClear; $j++) {
            $currentY = [Console]::CursorTop - 1
            if ($currentY -lt $startLine) { break }
            [Console]::SetCursorPosition(0, $currentY)
            Write-Host (" " * [Math]::Min($host.UI.RawUI.WindowSize.Width, 120)) -NoNewline
        }
        [Console]::SetCursorPosition(0, $startLine)

        switch ($key) {
            38 { $selected = if ($selected -gt 0) { $selected - 1 } else { $total - 1 } }         # Up
            40 { $selected = if ($selected -lt $total - 1) { $selected + 1 } else { 0 } }         # Down
            13 { if ($multi) { return @($checkedList.Keys | ForEach-Object { [int]$_ }) }          # Enter
                 else { return $selected } }
            32 { if ($multi) { if ($checkedList[$selected]) { $checkedList.Remove($selected) }    # Space
                              else { $checkedList[$selected] = $true } } }
            65 { if ($multi) { for ($k = 0; $k -lt $total; $k++) { $checkedList[$k] = $true } } } # A
            81 { exit 0 }                                                                          # Q
        }
    }
}

# ═══════════════════ SILENT MODE ═══════════════════
if ($Force -or ($All -and $AllSkills)) {
    if (-not (Test-Path "$repoDir\.git")) {
        git clone $repoUrl $repoDir 2>&1 | Out-Null
    } else {
        git -C $repoDir pull 2>&1 | Out-Null
    }
    $repoSkills = @{}
    Get-ChildItem $skillsRoot -Directory | ForEach-Object {
        $cat = $_.Name
        Get-ChildItem $_.FullName -Directory | ForEach-Object { $repoSkills[$_.Name] = $_.FullName }
    }
    if ($Skills) { $names = $Skills -split ',' | ForEach-Object { $_.Trim() } }
    else { $names = $repoSkills.Keys }

    $targets = if ($Force -or $All) { $platforms }
    else {
        @()
        if ($OpenCode) { $platforms[0]; if ($OpenCode) { $platforms | Where-Object key -eq "opencode" } }
        # simplified
        foreach ($p in $platforms) {
            if (($p.key -eq "opencode" -and $OpenCode) -or ($p.key -eq "claude" -and $Claude) -or
                ($p.key -eq "codex" -and $Codex) -or ($p.key -eq "cursor" -and $Cursor) -or
                ($p.key -eq "gemini" -and $Gemini) -or ($p.key -eq "copilot" -and $Copilot) -or
                ($p.key -eq "windsurf" -and $Windsurf)) { $p }
        }
    }

    foreach ($p in $targets) {
        New-Item -ItemType Directory -Path $p.dir -Force | Out-Null
        foreach ($name in $names) {
            if (-not $repoSkills[$name]) { continue }
            $link = "$($p.dir)\$name"
            if (Test-Path $link) { Remove-Item $link -Recurse -Force }
            New-Item -ItemType Junction -Path $link -Target $repoSkills[$name] | Out-Null
        }
        Write-Host (ac green "  + $($p.key): $($names.Count) skills")
    }
    git -C $repoDir rev-parse HEAD | Out-File $versionFile -Encoding ascii -NoNewline
    Write-Host (ac magenta "`n  Done. Restart your AI coding tool to load the new skills.")
    exit 0
}

# ═══════════════════ STATUS MODE ═══════════════════
if ($Status) {
    banner "Status"
    if (-not (Test-Path "$repoDir\.git")) {
        Write-Host (ac red "  Not installed yet. Run without -Status to install."); exit 1
    }
    git -C $repoDir pull 2>&1 | Out-Null
    $repoSkills = @{}
    Get-ChildItem $skillsRoot -Directory | ForEach-Object {
        Get-ChildItem $_.FullName -Directory | ForEach-Object { $repoSkills[$_.Name] = $_.FullName }
    }
    foreach ($p in $platforms) {
        Write-Host (ac cyan "`n  [$($p.label)]  $($p.dir)")
        if (Test-Path $p.dir) {
            $found = @(Get-ChildItem $p.dir -Directory -ErrorAction SilentlyContinue | Where-Object { $repoSkills.ContainsKey($_.Name) })
            if ($found.Count -gt 0) {
                foreach ($f in $found) {
                    $link = $false
                    try { $item = Get-Item $f.FullName -Force; $link = ($item.Attributes -band 0x400) -eq 0x400 } catch {}
                    $icon = if ($link) { (ac green "  +") } else { (ac yellow "  ?") }
                    Write-Host "$icon $($f.Name)"
                }
            } else { Write-Host (ac gray "      (none)") }
        } else { Write-Host (ac gray "      (not detected)") }
    }
    Write-Host ""; exit 0
}

# ═══════════════════ MAIN TUI ═══════════════════
banner "Installer"

# ─── Sync repo ───
if (-not (Test-Path "$repoDir\.git")) {
    Write-Host (ac yellow "  Cloning LFen-Skills...") -NoNewline
    git clone $repoUrl $repoDir 2>&1 | Out-Null
    Write-Host (ac green " Done")
} else {
    $lastHash = if (Test-Path $versionFile) { (Get-Content $versionFile).Trim() } else { "" }
    Write-Host (ac yellow "  Updating LFen-Skills...") -NoNewline
    git -C $repoDir pull 2>&1 | Out-Null
    $currentHash = (git -C $repoDir rev-parse HEAD).Trim()
    if ($lastHash -and $lastHash -ne $currentHash) {
        Write-Host (ac green " Done")
        $log = git -C $repoDir log --oneline "$lastHash..$currentHash" 2>&1
        if ($log) {
            Write-Host (ac cyan "  Updated:")
            $log | ForEach-Object { Write-Host (ac gray "    $_") }
        }
    } else {
        Write-Host (ac green " Done")
    }
}
Write-Host ""

# ─── Discover skills ───
$repoSkills = @{}
Get-ChildItem $skillsRoot -Directory | ForEach-Object {
    $cat = $_.Name
    Get-ChildItem $_.FullName -Directory | ForEach-Object { $repoSkills[$_.Name] = @{ Path = $_.FullName; Category = $cat } }
}

# ─── Build platform menu with live detection ───
$platMenu = @()
foreach ($p in $platforms) {
    $detected = Test-Path $p.dir
    $installed = $false
    if ($detected) {
        $installed = @(Get-ChildItem $p.dir -Directory -ErrorAction SilentlyContinue | Where-Object { $repoSkills.ContainsKey($_.Name) }).Count -gt 0
    }
    $tag = if ($installed) { (ac green " • installed") }
           elseif ($detected) { (ac gray " • detected") }
           else { (ac gray " • not found") }

    $platMenu += @{
        label = $p.label
        key   = $p.key
        dir   = $p.dir
        note  = $p.note
        extra = $tag
    }
}

# ─── UPDATE MODE ───
if ($Update) {
    $idx = Show-Menu "Select platform to update:" $platMenu $false $null
    $plat = $platforms[$idx]

    $installedMenu = @()
    if (Test-Path $plat.dir) {
        Get-ChildItem $plat.dir -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            if ($repoSkills.ContainsKey($_.Name)) {
                $installedMenu += @{ label = $_.Name; extra = $repoSkills[$_.Name].Category; note = "" }
            }
        }
    }
    if ($installedMenu.Count -eq 0) {
        Write-Host (ac red "`n  No LFen skills installed on $($plat.label). Use install mode."); exit 1
    }

    $checked = @{}
    $selectedIdx = Show-Menu "Select skills to update (Space = toggle):" $installedMenu $true $checked

    if ($selectedIdx.Count -eq 0) { Write-Host (ac gray "`n  Nothing selected."); exit 0 }

    Write-Host (ac yellow "`n  Updating on $($plat.label)...")
    foreach ($i in $selectedIdx) {
        $s = $installedMenu[$i]
        $link = "$($plat.dir)\$($s.label)"
        Remove-Item $link -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Junction -Path $link -Target $repoSkills[$s.label].Path | Out-Null
        Write-Host (ac green "    + $($s.label)")
    }
    git -C $repoDir rev-parse HEAD | Out-File $versionFile -Encoding ascii -NoNewline
    Write-Host (ac green "`n  Done.`n")
    exit 0
}

# ─── INSTALL MODE: Step 1 - Platform ───
$idx = Show-Menu "Select target platform:" $platMenu $false $null
$selectedPlat = @($platforms[$idx])

# ─── INSTALL MODE: Step 2 - Skills ───
$skillMenu = @()
foreach ($name in ($repoSkills.Keys | Sort-Object)) {
    $skillMenu += @{ label = $name; extra = $repoSkills[$name].Category; note = "" }
}

$checked = @{}
$selectedSkillIdx = Show-Menu "Select skills to install (Space = toggle, A = all):" $skillMenu $true $checked
if ($selectedSkillIdx.Count -eq 0) { Write-Host (ac gray "`n  Nothing selected."); exit 0 }
$selectedSkills = $selectedSkillIdx | ForEach-Object { $skillMenu[$_] }

# ─── Install ───
Clear-Host
banner "Installer"
Write-Host (ac yellow "  Installing...`n")

foreach ($plat in $selectedPlat) {
    New-Item -ItemType Directory -Path $plat.dir -Force | Out-Null
    Write-Host (ac cyan "  $($plat.label)")

    foreach ($skill in $selectedSkills) {
        $link = "$($plat.dir)\$($skill.label)"
        if (Test-Path $link) { Remove-Item $link -Recurse -Force -ErrorAction SilentlyContinue }
        New-Item -ItemType Junction -Path $link -Target $repoSkills[$skill.label].Path | Out-Null
        Write-Host (ac green "    + $($skill.label)") -NoNewline
        Write-Host (ac gray " [$($skill.extra)]")
    }
    Write-Host ""
}

git -C $repoDir rev-parse HEAD | Out-File $versionFile -Encoding ascii -NoNewline

$sc = $selectedSkills.Count; $pc = $selectedPlat.Count
Write-Host (ac green "  Installed $sc skills to $pc platform(s).")
Write-Host (ac magenta "  Restart your AI coding tool to load the new skills.`n")