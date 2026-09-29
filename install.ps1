# LFen Skills - Terminal UI Installer
# Online:  iwr https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.ps1 | iex
# Local:   .\install.ps1
# Silent:  .\install.ps1 -All -AllSkills -Force
#          .\install.ps1 -Claude -Codex -Skills "skill1,skill2"   (only the platforms named)
# Status:  .\install.ps1 -Status   (same rules as scripts/check_install_links.py)

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
try { $host.UI.RawUI.CursorSize = 0 } catch {}  # not every host has a console cursor

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
# Not "ac": that is the built-in alias of Add-Content, and an alias wins over a function, so
# every coloured line used to print nothing and append its text to a file named after the colour.
function Paint($c, $t) { "$($ansi[$c])$t$($ansi.reset)" }

# Every non-ASCII glyph is built from its code point so this file stays ASCII: Windows
# PowerShell 5.1 reads a script without a BOM in the system code page (GBK on Chinese
# Windows), which splits UTF-8 bytes and breaks parsing; a BOM would fix that but breaks
# `iwr ... | iex`, where the BOM arrives as a character in front of param().
$glyph = @{ pointer = [char]0x203A; check = [char]0x2713; up = [char]0x2191; down = [char]0x2193; dot = [char]0x2022 }

function banner($mode) {
    Clear-Host
    Write-Host ""
    # Box-drawing art kept as ASCII placeholders and mapped back at run time (why: see $glyph).
    $box = @{ '#' = [char]0x2588; '[' = [char]0x2554; ']' = [char]0x2557; '{' = [char]0x255A; '}' = [char]0x255D; '=' = [char]0x2550; '|' = [char]0x2551 }
    foreach ($row in @(
        "##]     #######]#######]###]   ##]",
        "##|     ##[====}##[====}####]  ##|",
        "##|     #####]  #####]  ##[##] ##|",
        "##|     ##[==}  ##[==}  ##|{##]##|",
        "#######]##|     #######]##| {####|",
        "{======}{=}     {======}{=}  {===}"
    )) {
        $line = -join ($row.ToCharArray() | ForEach-Object { if ($box.ContainsKey([string]$_)) { $box[[string]$_] } else { $_ } })
        Write-Host (Paint cyan "  $line")
    }
    Write-Host (Paint yellow "  Skills $mode")
    Write-Host ""
}

# --- Platforms ---
$platforms = @(
    @{key="opencode"; label="OpenCode";           dir="$env:USERPROFILE\.agents\skills";          note="also covers Cline/Warp/Zed/Kilo +17 more"}
    @{key="claude";   label="Claude Code";        dir="$env:USERPROFILE\.claude\skills";           note=""}
    @{key="codex";    label="Codex";              dir="$env:USERPROFILE\.codex\skills";            note=""}
    @{key="cursor";   label="Cursor";             dir="$env:USERPROFILE\.cursor\skills";           note=""}
    @{key="gemini";   label="Gemini CLI";         dir="$env:USERPROFILE\.gemini\skills";           note=""}
    @{key="copilot";  label="GitHub Copilot";     dir="$env:USERPROFILE\.copilot\skills";          note=""}
    @{key="windsurf"; label="Windsurf";           dir="$env:USERPROFILE\.codeium\windsurf\skills"; note=""}
)

# --- Arrow-key menu engine ---
function Show-Menu($title, $items, $multi, $checkedList) {
    $selected = 0; $total = $items.Count

    while ($true) {
        $startLine = [Console]::CursorTop
        if ($title) { Write-Host (Paint yellow "  $title") }

        for ($i = 0; $i -lt $total; $i++) {
            $cursor = if ($i -eq $selected) { (Paint cyan "  $($glyph.pointer)") } else { "   " }
            $name = if ($i -eq $selected) { (Paint cyan $items[$i].label) } else { $items[$i].label }

            $chk = ""
            if ($multi) {
                $chk = if ($checkedList[$i]) { (Paint cyan "[$($glyph.check)] ") } else { "[ ] " }
            }

            $extra = @()
            if ($items[$i].extra) { $extra += $items[$i].extra }
            if ($items[$i].note) { $extra += (Paint gray "($($items[$i].note))") }
            if ($items[$i].status) { $extra += $items[$i].status }

            $line = "$cursor $chk$name"
            if ($extra.Count -gt 0) { $line += "  " + ($extra -join "  ") }
            Write-Host $line
        }

        if ($multi) {
            Write-Host (Paint gray "`n  [$($glyph.up)$($glyph.down)] Navigate  [Space] Toggle  [a] Select All  [Enter] Confirm  [q] Quit")
        } else {
            Write-Host (Paint gray "`n  [$($glyph.up)$($glyph.down)] Navigate  [Enter] Select  [q] Quit")
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

# --- Git, catalog and entry rules ---
# Same rules as scripts/check_install_links.py:
#   catalog      every directory under skills\ that holds a SKILL.md
#   missing      a catalog skill with no entry on a platform that has LFen skills installed
#   dangling     a link whose target no longer exists, whoever created it
#   copy         a real directory named like a catalog skill (git pull never updates it)
#   wrong target a link named like a catalog skill that does not point at it in the clone,
#                or a link into the clone that does not point at a catalog skill
function Invoke-Git {
    # Windows PowerShell turns git's progress on stderr into errors under "Stop".
    $saved = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { $out = & git @args 2>$null } finally { $ErrorActionPreference = $saved }
    return $out
}

function Sync-Repo {
    if (-not (Test-Path "$repoDir\.git")) {
        Invoke-Git clone $repoUrl $repoDir | Out-Null
    } else {
        Invoke-Git -C $repoDir pull | Out-Null
    }
    if (-not (Test-Path "$repoDir\.git")) {
        Write-Host (Paint red "  Could not clone $repoUrl into $repoDir."); exit 1
    }
}

function Save-Version {
    Invoke-Git -C $repoDir rev-parse HEAD | Out-File $versionFile -Encoding ascii -NoNewline
}

function Get-CatalogSkills {
    $catalog = @{}
    if (-not (Test-Path -LiteralPath $skillsRoot)) { return $catalog }
    $root = [IO.Path]::GetFullPath($skillsRoot).TrimEnd('\')
    Get-ChildItem -LiteralPath $skillsRoot -Recurse -Filter SKILL.md -File | Sort-Object FullName | ForEach-Object {
        $dir = $_.Directory
        if (-not $catalog.ContainsKey($dir.Name)) {
            $category = $dir.Parent.FullName.Substring($root.Length).TrimStart('\') -replace '\\', '/'
            $catalog[$dir.Name] = @{ Path = $dir.FullName; Category = $category }
        }
    }
    return $catalog
}

function Test-IsLink($item) { return [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint) }

function Get-LinkTarget($item) {
    $target = @($item.Target | Where-Object { $_ }) | Select-Object -First 1
    if (-not $target) { return $null }
    $target = "$target" -replace '^\\\\\?\\', ''
    if (-not [IO.Path]::IsPathRooted($target)) { $target = Join-Path (Split-Path -Parent $item.FullName) $target }
    return [IO.Path]::GetFullPath($target)
}

function Get-NormalPath($path) { return [IO.Path]::GetFullPath($path).TrimEnd('\') }

function Test-SamePath($first, $second) {
    return [string]::Equals((Get-NormalPath $first), (Get-NormalPath $second), [StringComparison]::OrdinalIgnoreCase)
}

function Test-InsideSkillsRoot($path) {
    return (Get-NormalPath $path).StartsWith((Get-NormalPath $skillsRoot) + '\', [StringComparison]::OrdinalIgnoreCase)
}

# Removes the link itself, never what it points at.
function Remove-Link($path) { [IO.Directory]::Delete($path, $false) }

function Install-SkillLink($dir, $name, $targetPath) {
    $link = Join-Path $dir $name
    $existing = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
    if ($existing) {
        if (-not (Test-IsLink $existing)) {
            Write-Host (Paint yellow "    ! $name is a real directory in $dir; left in place (move it away, then rerun)")
            return $false
        }
        Remove-Link $link
    }
    New-Item -ItemType Junction -Path $link -Target $targetPath | Out-Null
    return $true
}

# Links into the install clone are the installer's own: one named like a catalog skill that
# does not reach it (the skill moved) is linked again; any other (the skill was renamed or
# removed, or was never a skill) is unlinked. Links pointing anywhere else are left alone.
function Repair-CloneLinks($dir, $catalog) {
    if (-not (Test-Path -LiteralPath $dir)) { return }
    foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction SilentlyContinue)) {
        if (-not (Test-IsLink $item)) { continue }
        $target = Get-LinkTarget $item
        if (-not $target -or -not (Test-InsideSkillsRoot $target)) { continue }
        if ($catalog.ContainsKey($item.Name)) {
            $expected = $catalog[$item.Name].Path
            if ((Test-Path -LiteralPath $target) -and (Test-SamePath $target $expected)) { continue }
            if (Install-SkillLink $dir $item.Name $expected) {
                Write-Host (Paint yellow "    ~ relinked $($item.Name) -> $expected")
            }
        } else {
            Remove-Link $item.FullName
            Write-Host (Paint yellow "    - removed $($item.Name) -> $target (not a catalog skill)")
        }
    }
}

function Get-EntryReport($dir, $catalog, [bool]$requireAll) {
    $findings = New-Object System.Collections.ArrayList
    $present = @{}; $ok = 0; $installed = $false
    $exists = Test-Path -LiteralPath $dir
    if ($exists) {
        foreach ($item in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction SilentlyContinue | Sort-Object Name)) {
            $name = $item.Name
            $known = $catalog.ContainsKey($name)
            if (Test-IsLink $item) {
                $target = Get-LinkTarget $item
                $intoClone = [bool]($target -and (Test-InsideSkillsRoot $target))
                if ($known) { $present[$name] = $true }
                if ($known -or $intoClone) { $installed = $true }
                if (-not $target -or -not (Test-Path -LiteralPath $target)) {
                    [void]$findings.Add(@{ Kind = "dangling"; Name = $name; Detail = "-> $target" })
                } elseif ($known) {
                    if (Test-SamePath $target $catalog[$name].Path) { $ok++ }
                    else { [void]$findings.Add(@{ Kind = "wrong target"; Name = $name; Detail = "-> $target (expected $($catalog[$name].Path))" }) }
                } elseif ($intoClone) {
                    [void]$findings.Add(@{ Kind = "wrong target"; Name = $name; Detail = "-> $target (not a catalog skill)" })
                }
            } elseif ($item.PSIsContainer -and $known) {
                $present[$name] = $true; $installed = $true
                [void]$findings.Add(@{ Kind = "copy"; Name = $name; Detail = "(real directory; git pull never updates it)" })
            }
        }
    }
    if ($installed -or $requireAll) {
        foreach ($name in ($catalog.Keys | Sort-Object)) {
            if (-not $present.ContainsKey($name)) { [void]$findings.Add(@{ Kind = "missing"; Name = $name; Detail = "" }) }
        }
    }
    return @{ Exists = $exists; Installed = $installed; Ok = $ok; Findings = @($findings) }
}

function Get-CloneStatus {
    $head = Invoke-Git -C $repoDir rev-parse --short HEAD
    if ($LASTEXITCODE -ne 0) { return "not a git clone; cannot tell whether it is behind" }
    Invoke-Git -C $repoDir fetch --quiet | Out-Null
    $note = if ($LASTEXITCODE -ne 0) { "; fetch failed, compared with the last fetched state" } else { "" }
    $counts = Invoke-Git -C $repoDir rev-list --left-right --count 'HEAD...@{upstream}'
    if ($LASTEXITCODE -ne 0 -or -not $counts) { return "HEAD $head, no upstream branch$note" }
    $parts = "$counts".Trim() -split '\s+'
    $state = if ([int]$parts[1] -gt 0) { "behind the remote by $($parts[1]) commit(s); run: git -C `"$repoDir`" pull" }
             else { "up to date with the remote" }
    if ([int]$parts[0] -gt 0) { $state += ", $($parts[0]) local commit(s) not pushed" }
    return "HEAD $head, $state$note"
}

# =================== STATUS MODE ===================
if ($Status) {
    banner "Status"
    if (-not (Test-Path "$repoDir\.git")) {
        Write-Host (Paint red "  Not installed yet. Run without -Status to install."); exit 1
    }
    $catalog = Get-CatalogSkills
    Write-Host (Paint gray "  Install clone: $repoDir ($($catalog.Count) skills, $(Get-CloneStatus))")
    $problems = 0
    foreach ($p in $platforms) {
        $report = Get-EntryReport $p.dir $catalog $false
        Write-Host (Paint cyan "`n  [$($p.label)]  $($p.dir)")
        if ($report.Findings.Count -eq 0 -and -not $report.Exists) { Write-Host (Paint gray "      (not detected)"); continue }
        if ($report.Findings.Count -eq 0 -and -not $report.Installed) { Write-Host (Paint gray "      (no LFen skills installed)"); continue }
        Write-Host (Paint green "      $($report.Ok) ok")
        foreach ($f in $report.Findings) {
            Write-Host ("    " + (Paint yellow ("! {0,-13}" -f $f.Kind)) + " $($f.Name) $($f.Detail)")
        }
        $problems += $report.Findings.Count
    }
    if ($problems -gt 0) {
        Write-Host (Paint yellow "`n  $problems problem(s). Rerun the installer or -Update to relink; move real directories away first.`n")
        exit 1
    }
    Write-Host (Paint green "`n  No problems found.`n"); exit 0
}

# =================== SILENT MODE ===================
$switchOn = @{ opencode = $OpenCode; claude = $Claude; codex = $Codex; cursor = $Cursor
               gemini = $Gemini; copilot = $Copilot; windsurf = $Windsurf }
$chosen = @($platforms | Where-Object { $All -or $switchOn[$_.key] })
if (-not $Update -and ($Force -or $All -or $AllSkills -or $Skills -or $chosen.Count -gt 0)) {
    if ($chosen.Count -eq 0) {
        Write-Host (Paint red "  No platform selected. Add -All, or platform switches such as -Claude -Codex."); exit 1
    }
    Sync-Repo
    $catalog = Get-CatalogSkills
    $names = @($catalog.Keys | Sort-Object)
    if ($Skills) {
        $asked = @($Skills -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        $unknown = @($asked | Where-Object { -not $catalog.ContainsKey($_) })
        if ($unknown.Count -gt 0) { Write-Host (Paint yellow "  ! not in the catalog, skipped: $($unknown -join ', ')") }
        $names = @($asked | Where-Object { $catalog.ContainsKey($_) })
    }
    foreach ($p in $chosen) {
        New-Item -ItemType Directory -Path $p.dir -Force | Out-Null
        Repair-CloneLinks $p.dir $catalog
        $count = 0
        foreach ($name in $names) { if (Install-SkillLink $p.dir $name $catalog[$name].Path) { $count++ } }
        Write-Host (Paint green "  + $($p.key): $count skills")
    }
    Save-Version
    Write-Host (Paint magenta "`n  Done. Restart your AI coding tool to load the new skills.")
    exit 0
}

# =================== MAIN TUI ===================
banner "Installer"

# --- Sync repo ---
if (-not (Test-Path "$repoDir\.git")) {
    Write-Host (Paint yellow "  Cloning LFen-Skills...") -NoNewline
    Sync-Repo
    Write-Host (Paint green " Done")
} else {
    $lastHash = if (Test-Path $versionFile) { (Get-Content $versionFile).Trim() } else { "" }
    Write-Host (Paint yellow "  Updating LFen-Skills...") -NoNewline
    Sync-Repo
    $currentHash = "$(Invoke-Git -C $repoDir rev-parse HEAD)".Trim()
    if ($lastHash -and $lastHash -ne $currentHash) {
        Write-Host (Paint green " Done")
        $log = Invoke-Git -C $repoDir log --oneline "$lastHash..$currentHash"
        if ($log) {
            Write-Host (Paint cyan "  Updated:")
            $log | ForEach-Object { Write-Host (Paint gray "    $_") }
        }
    } else {
        Write-Host (Paint green " Done")
    }
}
Write-Host ""

# --- Discover skills ---
$repoSkills = Get-CatalogSkills

# --- Build platform menu with live detection ---
$platMenu = @()
foreach ($p in $platforms) {
    $detected = Test-Path $p.dir
    $installed = $detected -and (Get-EntryReport $p.dir $repoSkills $false).Installed
    $tag = if ($installed) { (Paint green " $($glyph.dot) installed") }
           elseif ($detected) { (Paint gray " $($glyph.dot) detected") }
           else { (Paint gray " $($glyph.dot) not found") }

    $platMenu += @{
        label = $p.label
        key   = $p.key
        dir   = $p.dir
        note  = $p.note
        extra = $tag
    }
}

# --- UPDATE MODE ---
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
        Write-Host (Paint red "`n  No LFen skills installed on $($plat.label). Use install mode."); exit 1
    }

    $checked = @{}
    $selectedIdx = Show-Menu "Select skills to update (Space = toggle):" $installedMenu $true $checked

    if ($selectedIdx.Count -eq 0) { Write-Host (Paint gray "`n  Nothing selected."); exit 0 }

    Write-Host (Paint yellow "`n  Updating on $($plat.label)...")
    Repair-CloneLinks $plat.dir $repoSkills
    foreach ($i in $selectedIdx) {
        $s = $installedMenu[$i]
        if (Install-SkillLink $plat.dir $s.label $repoSkills[$s.label].Path) {
            Write-Host (Paint green "    + $($s.label)")
        }
    }
    Save-Version
    Write-Host (Paint green "`n  Done.`n")
    exit 0
}

# --- INSTALL MODE: Step 1 - Platform ---
$idx = Show-Menu "Select target platform:" $platMenu $false $null
$selectedPlat = @($platforms[$idx])

# --- INSTALL MODE: Step 2 - Skills ---
$skillMenu = @()
foreach ($name in ($repoSkills.Keys | Sort-Object)) {
    $skillMenu += @{ label = $name; extra = $repoSkills[$name].Category; note = "" }
}

$checked = @{}
$selectedSkillIdx = Show-Menu "Select skills to install (Space = toggle, A = all):" $skillMenu $true $checked
if ($selectedSkillIdx.Count -eq 0) { Write-Host (Paint gray "`n  Nothing selected."); exit 0 }
$selectedSkills = @($selectedSkillIdx | ForEach-Object { $skillMenu[$_] })

# --- Install ---
Clear-Host
banner "Installer"
Write-Host (Paint yellow "  Installing...`n")

foreach ($plat in $selectedPlat) {
    New-Item -ItemType Directory -Path $plat.dir -Force | Out-Null
    Write-Host (Paint cyan "  $($plat.label)")
    Repair-CloneLinks $plat.dir $repoSkills

    foreach ($skill in $selectedSkills) {
        if (-not (Install-SkillLink $plat.dir $skill.label $repoSkills[$skill.label].Path)) { continue }
        Write-Host (Paint green "    + $($skill.label)") -NoNewline
        Write-Host (Paint gray " [$($skill.extra)]")
    }
    Write-Host ""
}

Save-Version

$sc = $selectedSkills.Count; $pc = $selectedPlat.Count
Write-Host (Paint green "  Installed $sc skills to $pc platform(s).")
Write-Host (Paint magenta "  Restart your AI coding tool to load the new skills.`n")
