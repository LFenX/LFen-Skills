#!/usr/bin/env bash
# LFen Skills 安装/更新 (Linux / macOS)
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
#   bash install.sh                          # 交互式安装
#   bash install.sh --status                 # 查看当前状态（规则同 scripts/check_install_links.py）
#   bash install.sh --update                 # 交互式更新
#   bash install.sh --update --all-skills    # 更新全部已有skill
#   bash install.sh --all --all-skills       # 全平台 + 全skill
#   bash install.sh --cursor --skills "skill1,skill2"

set -euo pipefail

REPO_URL="https://github.com/LFenX/LFen-Skills.git"
REPO_DIR="$HOME/.lfenskills"
SKILLS_ROOT="$REPO_DIR/skills"
VERSION_FILE="$HOME/.lfenskills-version"

declare -A TARGETS
TARGETS=(
    [opencode]="$HOME/.agents/skills"
    [claude]="$HOME/.claude/skills"
    [codex]="$HOME/.codex/skills"
    [cursor]="$HOME/.cursor/skills"
    [gemini]="$HOME/.gemini/skills"
    [copilot]="$HOME/.copilot/skills"
    [windsurf]="$HOME/.codeium/windsurf/skills"
)
PLATFORM_ORDER=(opencode claude codex cursor gemini copilot windsurf)

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; DARK='\033[2m'; NC='\033[0m'

MODE="install"
ALL=false; OPENCODE=false; CLAUDE=false; CODEX=false
CURSOR=false; GEMINI=false; COPILOT=false; WINDSURF=false
ALL_SKILLS=false; SKILLS_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)            ALL=true ;;
        --opencode)       OPENCODE=true ;;
        --claude)         CLAUDE=true ;;
        --codex)          CODEX=true ;;
        --cursor)         CURSOR=true ;;
        --gemini)         GEMINI=true ;;
        --copilot)        COPILOT=true ;;
        --windsurf)       WINDSURF=true ;;
        --all-skills)     ALL_SKILLS=true ;;
        --skills)         SKILLS_FILTER="$2"; shift ;;
        --update|-u)      MODE="update" ;;
        --status|-s)      MODE="status" ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
    esac
    shift
done

LABEL="Installer"
[ "$MODE" = "update" ] && LABEL="Updater"
[ "$MODE" = "status" ] && LABEL="Status"

echo -e "\n${CYAN}  LFen Skills $LABEL${NC}\n"

# ========== Step 1: sync repo ==========
if [ "$MODE" = "status" ]; then
    if [ ! -d "$REPO_DIR/.git" ]; then
        echo -e "${RED}  Not installed yet. Run without --status to install.${NC}\n"; exit 1
    fi
elif [ ! -d "$REPO_DIR/.git" ]; then
    echo -e "${YELLOW}[sync] Cloning LFen-Skills...${NC}"
    rm -rf "$REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR" > /dev/null 2>&1
else
    LAST_HASH=""
    [ -f "$VERSION_FILE" ] && LAST_HASH=$(cat "$VERSION_FILE" 2>/dev/null || echo "")

    git -C "$REPO_DIR" pull > /dev/null 2>&1
    CURRENT_HASH=$(git -C "$REPO_DIR" rev-parse HEAD)

    if [ -n "$LAST_HASH" ] && [ "$LAST_HASH" != "$CURRENT_HASH" ]; then
        LOG=$(git -C "$REPO_DIR" log --oneline "$LAST_HASH..$CURRENT_HASH" 2>/dev/null || echo "")
        if [ -n "$LOG" ]; then
            echo -e "${CYAN}  Updated commits:${NC}"
            echo "$LOG" | while read -r line; do echo -e "    ${DARK}$line${NC}"; done
        fi
    fi
fi

# ========== discover repo skills: every directory holding a SKILL.md ==========
declare -A SKILL_PATHS SKILL_CATEGORIES
while IFS= read -r -d '' skill_file; do
    dir=$(dirname "$skill_file")
    name=$(basename "$dir")
    [ -n "${SKILL_PATHS[$name]+x}" ] && continue
    rel="${dir#"$SKILLS_ROOT"/}"
    SKILL_PATHS[$name]="$dir"
    SKILL_CATEGORIES[$name]=$(dirname "$rel")
done < <(find "$SKILLS_ROOT" -type f -name SKILL.md -print0 | sort -z)

ALL_NAMES=($(printf '%s\n' "${!SKILL_PATHS[@]}" | sort))
if [ ${#ALL_NAMES[@]} -eq 0 ]; then
    echo -e "${RED}No skills found in $SKILLS_ROOT${NC}"; exit 1
fi

# ========== entry rules ==========
# Same rules as scripts/check_install_links.py:
#   missing      a catalog skill with no entry on a platform that has LFen skills installed
#   dangling     a link whose target no longer exists, whoever created it
#   copy         a real directory named like a catalog skill (git pull never updates it)
#   wrong target a link named like a catalog skill that does not point at it in the clone,
#                or a link into the clone that does not point at a catalog skill
SKILLS_ROOT_REAL=$(cd -P "$SKILLS_ROOT" 2>/dev/null && pwd -P || echo "$SKILLS_ROOT")

is_catalog() { [ -n "${SKILL_PATHS[$1]+x}" ]; }

physical() { (cd -P "$1" 2>/dev/null && pwd -P); }

link_target() {
    local raw
    raw=$(readlink "$1")
    case "$raw" in
        /*) printf '%s\n' "$raw" ;;
        *)  printf '%s/%s\n' "$(dirname "$1")" "$raw" ;;
    esac
}

into_clone() {
    case "$1" in
        "$SKILLS_ROOT"/*|"$SKILLS_ROOT_REAL"/*) return 0 ;;
    esac
    return 1
}

remove_link() {  # the link itself, never what it points at
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) cmd.exe /c "rmdir \"$(cygpath -w "$1")\"" >/dev/null 2>&1 ;;
        *) rm -f "$1" ;;
    esac
}

make_link() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) cmd.exe /c "mklink /J \"$(cygpath -w "$2")\" \"$(cygpath -w "$1")\"" >/dev/null 2>&1 ;;
        *) ln -s "$1" "$2" ;;
    esac
}

# Link one skill into a platform directory; a real directory in the way is left alone.
install_link() {
    local link="$1/$2"
    if [ -L "$link" ]; then
        remove_link "$link"
    elif [ -e "$link" ]; then
        echo -e "   ${YELLOW}! $2 is a real directory in $1; left in place (move it away, then rerun)${NC}"
        return 1
    fi
    make_link "${SKILL_PATHS[$2]}" "$link"
}

# Links into the install clone are the installer's own: one named like a catalog skill that
# does not reach it (the skill moved) is linked again; any other (the skill was renamed or
# removed, or was never a skill) is unlinked. Links pointing anywhere else are left alone.
repair_clone_links() {
    local entry target name entries=()
    [ -d "$1" ] || return 0
    while IFS= read -r -d '' entry; do entries+=("$entry"); done < <(find "$1" -mindepth 1 -maxdepth 1 -print0)
    for entry in "${entries[@]+"${entries[@]}"}"; do
        [ -L "$entry" ] || continue
        target=$(link_target "$entry")
        into_clone "$target" || continue
        name=$(basename "$entry")
        if is_catalog "$name"; then
            if [ -e "$entry" ] && [ "$(physical "$entry")" = "$(physical "${SKILL_PATHS[$name]}")" ]; then continue; fi
            install_link "$1" "$name"
            echo -e "   ${YELLOW}~ relinked $name -> ${SKILL_PATHS[$name]}${NC}"
        else
            remove_link "$entry"
            echo -e "   ${YELLOW}- removed $name -> $target (not a catalog skill)${NC}"
        fi
    done
}

# Fills REPORT_OK, REPORT_INSTALLED and REPORT_LINES ("kind|name|detail") for one directory.
inspect_platform() {
    local dir="$1" require_all="$2" entry name target
    local -A present=()
    REPORT_OK=0; REPORT_INSTALLED=false; REPORT_LINES=()
    if [ -d "$dir" ]; then
        while IFS= read -r -d '' entry; do
            name=$(basename "$entry")
            if [ -L "$entry" ]; then
                target=$(link_target "$entry")
                if is_catalog "$name"; then present[$name]=1; fi
                if is_catalog "$name" || into_clone "$target"; then REPORT_INSTALLED=true; fi
                if [ ! -e "$entry" ]; then
                    REPORT_LINES+=("dangling|$name|-> $target")
                elif is_catalog "$name"; then
                    if [ "$(physical "$entry")" = "$(physical "${SKILL_PATHS[$name]}")" ]; then
                        REPORT_OK=$((REPORT_OK + 1))
                    else
                        REPORT_LINES+=("wrong target|$name|-> $target (expected ${SKILL_PATHS[$name]})")
                    fi
                elif into_clone "$target"; then
                    REPORT_LINES+=("wrong target|$name|-> $target (not a catalog skill)")
                fi
            elif [ -d "$entry" ] && is_catalog "$name"; then
                present[$name]=1; REPORT_INSTALLED=true
                REPORT_LINES+=("copy|$name|(real directory; git pull never updates it)")
            fi
        done < <(find "$dir" -mindepth 1 -maxdepth 1 -print0 | sort -z)
    fi
    if [ "$REPORT_INSTALLED" = true ] || [ "$require_all" = true ]; then
        for name in "${ALL_NAMES[@]}"; do
            [ -n "${present[$name]+x}" ] || REPORT_LINES+=("missing|$name|")
        done
    fi
}

clone_status() {
    local head counts ahead behind state note=""
    head=$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null) || { echo "not a git clone; cannot tell whether it is behind"; return 0; }
    git -C "$REPO_DIR" fetch --quiet > /dev/null 2>&1 || note="; fetch failed, compared with the last fetched state"
    counts=$(git -C "$REPO_DIR" rev-list --left-right --count 'HEAD...@{upstream}' 2>/dev/null) || { echo "HEAD $head, no upstream branch$note"; return 0; }
    read -r ahead behind <<< "$counts"
    state="up to date with the remote"
    if [ "$behind" -gt 0 ]; then state="behind the remote by $behind commit(s); run: git -C \"$REPO_DIR\" pull"; fi
    if [ "$ahead" -gt 0 ]; then state="$state, $ahead local commit(s) not pushed"; fi
    echo "HEAD $head, $state$note"
}

# ========== Status mode ==========
if [ "$MODE" = "status" ]; then
    echo -e "  ${DARK}Install clone: $REPO_DIR (${#ALL_NAMES[@]} skills, $(clone_status))${NC}"
    PROBLEMS=0
    for platform in "${PLATFORM_ORDER[@]}"; do
        dir="${TARGETS[$platform]}"
        inspect_platform "$dir" false
        echo -e "\n  ${CYAN}[$platform]${NC} $dir"
        if [ ${#REPORT_LINES[@]} -eq 0 ] && [ ! -d "$dir" ]; then
            echo -e "   ${DARK}(directory not found)${NC}"; continue
        fi
        if [ ${#REPORT_LINES[@]} -eq 0 ] && [ "$REPORT_INSTALLED" = false ]; then
            echo -e "   ${DARK}(no LFen skills installed)${NC}"; continue
        fi
        echo -e "   ${GREEN}$REPORT_OK ok${NC}"
        if [ ${#REPORT_LINES[@]} -gt 0 ]; then
            for line in "${REPORT_LINES[@]}"; do
                IFS='|' read -r kind name detail <<< "$line"
                printf "   ${YELLOW}! %-13s${NC} %s %s\n" "$kind" "$name" "$detail"
            done
        fi
        PROBLEMS=$((PROBLEMS + ${#REPORT_LINES[@]}))
    done
    if [ "$PROBLEMS" -gt 0 ]; then
        echo -e "\n${YELLOW}  $PROBLEMS problem(s). Rerun the installer or --update to relink; move real directories away first.${NC}\n"
        exit 1
    fi
    echo -e "\n${GREEN}  No problems found.${NC}\n"
    exit 0
fi

# ========== Update mode ==========
if [ "$MODE" = "update" ]; then
    for platform in "${PLATFORM_ORDER[@]}"; do
        repair_clone_links "${TARGETS[$platform]}"
    done
    echo -e "\n${YELLOW}  Installed skills (select to update):${NC}\n"

    declare -A FIRST_IDX IDX_NAME IDX_CAT IDX_PLATFORMS
    idx=1; seen=()

    for platform in "${PLATFORM_ORDER[@]}"; do
        dir="${TARGETS[$platform]}"; [ ! -d "$dir" ] && continue
        for name in "${ALL_NAMES[@]}"; do
            link="$dir/$name"
            if [ -L "$link" ]; then
                if [[ ! " ${seen[*]:-} " =~ " ${name} " ]]; then
                    seen+=("$name")
                    FIRST_IDX[$name]=$idx
                    IDX_NAME[$idx]="$name"
                    IDX_CAT[$idx]="${SKILL_CATEGORIES[$name]}"
                    IDX_PLATFORMS[$idx]=""
                    idx=$((idx + 1))
                fi
                i="${FIRST_IDX[$name]}"
                IDX_PLATFORMS[$i]="${IDX_PLATFORMS[$i]}$platform,"
            fi
        done
    done

    # strip trailing comma
    for k in "${!IDX_PLATFORMS[@]}"; do
        IDX_PLATFORMS[$k]=${IDX_PLATFORMS[$k]%,}
    done

    total=$((idx - 1))
    if [ "$total" -eq 0 ]; then
        echo -e "${RED}  No LFen skills currently installed. Use install mode instead.${NC}\n"
        exit 1
    fi

    if [ "$ALL_SKILLS" = true ]; then
        SELECTED_NAMES=("${seen[@]}")
    else
        for ((i=1; i<=total; i++)); do
            printf "  [$i] %s %s (%s)\n" "${IDX_NAME[$i]}" "[${IDX_CAT[$i]}]" "${IDX_PLATFORMS[$i]}"
        done
        echo "  [a] All"
        echo "  [f] Full reinstall (including missing skills)"
        echo ""
        read -rp "  Enter choice: " CHOICE

        if [ "$CHOICE" = "a" ]; then
            SELECTED_NAMES=("${seen[@]}")
        elif [ "$CHOICE" = "f" ]; then
            MODE="install"; ALL_SKILLS=true
        elif [[ "$CHOICE" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
            IFS=',' read -ra IDX <<< "$CHOICE"
            SELECTED_NAMES=()
            for i in "${IDX[@]}"; do
                i=$(echo "$i" | xargs)
                [ -n "${IDX_NAME[$i]:-}" ] && SELECTED_NAMES+=("${IDX_NAME[$i]}")
            done
        else
            echo -e "${RED}Invalid choice, exiting.${NC}"; exit 1
        fi
    fi

    if [ "$MODE" = "update" ] && [ "${#SELECTED_NAMES[@]}" -gt 0 ]; then
        echo -e "\n${YELLOW}  Updating...${NC}"
        for name in "${SELECTED_NAMES[@]}"; do
            for platform in "${PLATFORM_ORDER[@]}"; do
                link="${TARGETS[$platform]}/$name"
                if [ -L "$link" ] && install_link "${TARGETS[$platform]}" "$name"; then
                    echo -e "   ${GREEN}+ [$platform] $name${NC}"
                fi
            done
        done
        git -C "$REPO_DIR" rev-parse HEAD > "$VERSION_FILE"
        echo -e "\n${GREEN}  Update done.${NC}\n"
        exit 0
    fi
fi

# ========== Step 3: choose platforms ==========
HAS_FLAGS=false
$ALL && HAS_FLAGS=true
$OPENCODE && HAS_FLAGS=true
$CLAUDE && HAS_FLAGS=true
$CODEX && HAS_FLAGS=true
$CURSOR && HAS_FLAGS=true
$GEMINI && HAS_FLAGS=true
$COPILOT && HAS_FLAGS=true
$WINDSURF && HAS_FLAGS=true

if [ "$MODE" = "install" ] && ! $HAS_FLAGS; then
    echo -e "${YELLOW}  Select target platform(s):${NC}"
    echo "  [1] All (installs to all 7 unique paths below)"
    echo "  [2] OpenCode (.agents/skills)  -- also covers Cline, Warp, Zed, Kilo, Kimi, Droid, +14 more"
    echo "  [3] Claude Code (.claude/skills)"
    echo "  [4] Codex (.codex/skills)"
    echo "  [5] Cursor (.cursor/skills)"
    echo "  [6] Gemini CLI (.gemini/skills)"
    echo "  [7] GitHub Copilot (.copilot/skills)"
    echo "  [8] Windsurf (.codeium/windsurf/skills)"
    echo ""
    read -rp "  Enter choice (1-8): " CHOICE
    case "$CHOICE" in
        1) ALL=true ;;
        2) OPENCODE=true ;;
        3) CLAUDE=true ;;
        4) CODEX=true ;;
        5) CURSOR=true ;;
        6) GEMINI=true ;;
        7) COPILOT=true ;;
        8) WINDSURF=true ;;
        *) echo -e "${RED}Invalid choice, exiting.${NC}"; exit 1 ;;
    esac
fi

SELECTED_TARGETS=()
if [ "$ALL" = true ]; then
    SELECTED_TARGETS=("${PLATFORM_ORDER[@]}")
else
    [ "$OPENCODE" = true ] && SELECTED_TARGETS+=("opencode")
    [ "$CLAUDE" = true ]   && SELECTED_TARGETS+=("claude")
    [ "$CODEX" = true ]    && SELECTED_TARGETS+=("codex")
    [ "$CURSOR" = true ]   && SELECTED_TARGETS+=("cursor")
    [ "$GEMINI" = true ]   && SELECTED_TARGETS+=("gemini")
    [ "$COPILOT" = true ]  && SELECTED_TARGETS+=("copilot")
    [ "$WINDSURF" = true ] && SELECTED_TARGETS+=("windsurf")
fi

# ========== Step 4: choose skills ==========
if [ "$ALL_SKILLS" = true ]; then
    SELECTED_NAMES=("${ALL_NAMES[@]}")
elif [ -n "$SKILLS_FILTER" ]; then
    IFS=',' read -ra ASKED <<< "$SKILLS_FILTER"
    SELECTED_NAMES=()
    for name in "${ASKED[@]}"; do
        name=$(echo "$name" | xargs)
        [ -z "$name" ] && continue
        if is_catalog "$name"; then
            SELECTED_NAMES+=("$name")
        else
            echo -e "${YELLOW}  ! not in the catalog, skipped: $name${NC}"
        fi
    done
else
    echo -e "\n${YELLOW}  Select skills to install:${NC}"
    for i in "${!ALL_NAMES[@]}"; do
        idx=$((i + 1))
        printf "  [$idx] %s %s\n" "${ALL_NAMES[$i]}" "[${SKILL_CATEGORIES[${ALL_NAMES[$i]}]}]"
    done
    echo "  [a] All"
    echo ""
    read -rp "  Enter choice (number, comma-separated, or 'a'): " CHOICE

    if [ "$CHOICE" = "a" ]; then
        SELECTED_NAMES=("${ALL_NAMES[@]}")
    elif [[ "$CHOICE" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
        IFS=',' read -ra IDX <<< "$CHOICE"
        SELECTED_NAMES=()
        for i in "${IDX[@]}"; do
            i=$(echo "$i" | xargs)
            j=$((i - 1))
            [ -n "${ALL_NAMES[$j]:-}" ] && SELECTED_NAMES+=("${ALL_NAMES[$j]}")
        done
    else
        echo -e "${RED}Invalid choice, exiting.${NC}"; exit 1
    fi
fi

if [ ${#SELECTED_NAMES[@]} -eq 0 ]; then
    echo -e "${RED}No skills selected.${NC}"; exit 0
fi

# ========== Step 5: install ==========
echo -e "\n${YELLOW}  Installing...${NC}"

for platform in "${SELECTED_TARGETS[@]}"; do
    TARGET_DIR="${TARGETS[$platform]}"
    mkdir -p "$TARGET_DIR"
    repair_clone_links "$TARGET_DIR"
    for name in "${SELECTED_NAMES[@]}"; do
        if install_link "$TARGET_DIR" "$name"; then
            echo -e "   ${GREEN}+ [$platform] $name${NC}"
        fi
    done
done

git -C "$REPO_DIR" rev-parse HEAD > "$VERSION_FILE"

echo -e "\n${GREEN}  Done!${NC}"
for platform in "${SELECTED_TARGETS[@]}"; do
    echo -e "  $platform: ${#SELECTED_NAMES[@]} skills -> ${TARGETS[$platform]}"
done
echo -e "\n${MAGENTA}  Restart your AI coding tool to load the new skills.${NC}\n"
