#!/usr/bin/env bash
# LFen Skills 安装/更新 (Linux / macOS)
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/LFenX/LFen-Skills/main/install.sh | bash
#   bash install.sh                          # 交互式安装
#   bash install.sh --status                 # 查看当前状态
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
if [ ! -d "$REPO_DIR/.git" ]; then
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

# ========== discover repo skills ==========
declare -A SKILL_PATHS SKILL_CATEGORIES
while IFS= read -r -d '' dir; do
    name=$(basename "$dir")
    category=$(basename "$(dirname "$dir")")
    SKILL_PATHS[$name]="$dir"
    SKILL_CATEGORIES[$name]="$category"
done < <(find "$SKILLS_ROOT" -mindepth 2 -maxdepth 2 -type d -print0)

ALL_NAMES=($(printf '%s\n' "${!SKILL_PATHS[@]}" | sort))
if [ ${#ALL_NAMES[@]} -eq 0 ]; then
    echo -e "${RED}No skills found in $SKILLS_ROOT${NC}"; exit 1
fi

# ========== Status mode ==========
if [ "$MODE" = "status" ]; then
    echo -e "${YELLOW}  Skill status across platforms:${NC}\n"
    HAS=false
    for platform in "${!TARGETS[@]}"; do
        dir="${TARGETS[$platform]}"
        echo -e "  ${CYAN}[$platform]${NC}"
        if [ -d "$dir" ]; then
            found=false
            for name in "${ALL_NAMES[@]}"; do
                link="$dir/$name"
                if [ -L "$link" ] || [ -d "$link" ]; then
                    mark="+"
                    [ -L "$link" ] || mark="?"
                    echo -e "   $mark $name [${SKILL_CATEGORIES[$name]}]"
                    found=true; HAS=true
                fi
            done
            [ "$found" = false ] && echo -e "   ${DARK}(no LFen skills installed)${NC}"
        else
            echo -e "   ${DARK}(directory not found)${NC}"
        fi
    done
    if [ "$HAS" = false ]; then
        echo -e "${MAGENTA}\n  No skills installed yet. Run without --status to install.${NC}\n"
    fi
    exit 0
fi

# ========== Update mode ==========
if [ "$MODE" = "update" ]; then
    echo -e "\n${YELLOW}  Installed skills (select to update):${NC}\n"

    declare -A FIRST_IDX IDX_NAME IDX_CAT IDX_PLATFORMS
    idx=1; seen=()

    for platform in "${!TARGETS[@]}"; do
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

    if [ "${#SELECTED_NAMES[@]}" -gt 0 ]; then
        echo -e "\n${YELLOW}  Updating...${NC}"
        for name in "${SELECTED_NAMES[@]}"; do
            for platform in "${!TARGETS[@]}"; do
                link="${TARGETS[$platform]}/$name"
                if [ -L "$link" ]; then
                    rm -f "$link"
                    ln -s "${SKILL_PATHS[$name]}" "$link"
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
    SELECTED_TARGETS=("${!TARGETS[@]}")
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
    IFS=',' read -ra SELECTED_NAMES <<< "$SKILLS_FILTER"
    for i in "${!SELECTED_NAMES[@]}"; do SELECTED_NAMES[$i]=$(echo "${SELECTED_NAMES[$i]}" | xargs); done
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
    for name in "${SELECTED_NAMES[@]}"; do
        skill_dir="${SKILL_PATHS[$name]}"
        link="$TARGET_DIR/$name"
        if [ -L "$link" ] || [ -d "$link" ]; then rm -rf "$link"; fi

        case "$(uname -s)" in
            Linux|Darwin) ln -s "$skill_dir" "$link" ;;
            MINGW*|MSYS*|CYGWIN*) cmd.exe /c "mklink /J \"$(cygpath -w "$link")\" \"$(cygpath -w "$skill_dir")\"" >/dev/null 2>&1 ;;
        esac
        echo -e "   ${GREEN}+ [$platform] $name${NC}"
    done
done

git -C "$REPO_DIR" rev-parse HEAD > "$VERSION_FILE"

echo -e "\n${GREEN}  Done!${NC}"
for platform in "${SELECTED_TARGETS[@]}"; do
    echo -e "  $platform: ${#SELECTED_NAMES[@]} skills -> ${TARGETS[$platform]}"
done
echo -e "\n${MAGENTA}  Restart your AI coding tool to load the new skills.${NC}\n"