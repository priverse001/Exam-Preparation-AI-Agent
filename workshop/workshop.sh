#!/usr/bin/env bash
# ============================================================================
# Workshop Checkpoint Script
# ============================================================================
# Usage:
#   ./workshop/workshop.sh checkpoint N   Strip checkpoint N for implementation
#   ./workshop/workshop.sh solve N        Restore golden code for checkpoint N
#   ./workshop/workshop.sh reset          Restore all to golden
#   ./workshop/workshop.sh status         Show checkpoint states
#   ./workshop/create_scaffold_branch.sh  Create a local scaffold branch
#
# Checkpoints:
#   1  Implement a Tool          (search_uploaded_materials)
#   2  Agent + Handoffs          (CourseMaterialAgent + triage handoffs)
#   3  Structured Output + Prompt (TopicSummary + generate_topic_summary + prompt)
#   4  MCP Integration           (filesystem server + connection)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXERCISES_DIR="$SCRIPT_DIR/exercises"
GOLDEN_DIR="$SCRIPT_DIR/.golden"
SOLUTION_REF_FILE="$SCRIPT_DIR/.solution-ref"

# Each checkpoint maps to one or more exercise markers.
# Format: CHECKPOINT_ID:EXERCISE_ID:FILE:MARKER
CHECKPOINT_DEFS=(
    # Checkpoint 1: Tool
    "1:2:backend/app/agents_sdk/tools.py:EXERCISE_2"
    # Checkpoint 2: Agent + Handoffs
    "2:5:backend/app/agents_sdk/agents.py:EXERCISE_5"
    "2:6:backend/app/agents_sdk/agents.py:EXERCISE_6"
    # Checkpoint 3: Structured Output + Prompt
    "3:1:backend/app/agents_sdk/tools.py:EXERCISE_1"
    "3:4:backend/app/agents_sdk/tools.py:EXERCISE_4"
    "3:prompt:backend/app/agents_sdk/prompts.py:EXERCISE_PROMPT"
    # Checkpoint 4: MCP
    "4:7a:backend/app/agents_sdk/mcp.py:EXERCISE_7A"
    "4:7b:backend/app/agents_sdk/mcp.py:EXERCISE_7B"
)

CHECKPOINT_NAMES=(
    "1:Implement a Tool (search_uploaded_materials)"
    "2:Define Agent + Wire Handoffs"
    "3:Structured Output + Prompt Engineering"
    "4:MCP Integration (filesystem server)"
)

# ---- Helpers ---------------------------------------------------------------

get_checkpoint_entries() {
    local cp="$1"
    for def in "${CHECKPOINT_DEFS[@]}"; do
        if [[ "$def" == "$cp:"* ]]; then
            echo "$def"
        fi
    done
}

get_checkpoint_name() {
    local cp="$1"
    for entry in "${CHECKPOINT_NAMES[@]}"; do
        if [[ "$entry" == "$cp:"* ]]; then
            echo "${entry#*:}"
            return 0
        fi
    done
    echo "Checkpoint $cp"
}

get_checkpoint_files() {
    local cp="$1"
    while IFS= read -r entry; do
        echo "$(echo "$entry" | cut -d: -f3)"
    done < <(get_checkpoint_entries "$cp")
}

extract_golden_block() {
    local file="$1" marker="$2"
    local start_pat="# >>> ${marker}_START"
    local end_pat="# >>> ${marker}_END"
    sed -n "/${start_pat}/,/${end_pat}/p" "$file"
}

is_golden() {
    local file="$1" marker="$2"
    grep -q "# >>> ${marker}_START" "$file" 2>/dev/null
}

get_solution_ref() {
    if [[ -f "$SOLUTION_REF_FILE" ]]; then
        tr -d '\n' < "$SOLUTION_REF_FILE"
    else
        git -C "$PROJECT_DIR" rev-parse HEAD
    fi
}

strip_exercise() {
    local ex_id="$1" file="$2" marker="$3"
    local template="$EXERCISES_DIR/${ex_id}.txt"
    local start_pat="# >>> ${marker}_START"
    local end_pat="# >>> ${marker}_END"

    if [[ ! -f "$template" ]]; then
        echo "  Error: Template not found: $template" >&2
        return 1
    fi
    is_golden "$file" "$marker" || return 0

    mkdir -p "$GOLDEN_DIR"
    extract_golden_block "$file" "$marker" > "$GOLDEN_DIR/${ex_id}.golden"

    # Find the line number of the START marker (for restore)
    grep -n "$start_pat" "$file" | head -1 | cut -d: -f1 > "$GOLDEN_DIR/${ex_id}.startline"

    local tmpfile
    tmpfile=$(mktemp)
    local in_block=0
    while IFS= read -r line; do
        if [[ "$line" == *"$start_pat"* ]]; then
            in_block=1
            while IFS= read -r tline; do
                printf '%s\n' "$tline"
            done < "$template" >> "$tmpfile"
            continue
        fi
        if [[ "$line" == *"$end_pat"* ]]; then
            in_block=0
            continue
        fi
        if [[ $in_block -eq 0 ]]; then
            printf '%s\n' "$line" >> "$tmpfile"
        fi
    done < "$file"
    mv "$tmpfile" "$file"
}

restore_file_from_golden() {
    local rel_path="$1"
    local abs_path="${PROJECT_DIR}/${rel_path}"
    local solution_ref
    solution_ref="$(get_solution_ref)"

    if ! git -C "$PROJECT_DIR" show "${solution_ref}:${rel_path}" > "$abs_path" 2>/dev/null; then
        echo "Error: Failed to restore ${rel_path} from ${solution_ref}" >&2
        return 1
    fi
}

is_checkpoint_golden() {
    local cp="$1"
    while IFS= read -r entry; do
        local file="${PROJECT_DIR}/$(echo "$entry" | cut -d: -f3)"
        local marker
        marker=$(echo "$entry" | cut -d: -f4)
        is_golden "$file" "$marker" || return 1
    done < <(get_checkpoint_entries "$cp")
    return 0
}

get_active_checkpoint() {
    local cp
    for cp in 1 2 3 4; do
        if ! is_checkpoint_golden "$cp"; then
            echo "$cp"
            return 0
        fi
    done
    return 1
}

print_checkpoint_files() {
    local cp="$1"
    echo "   Files to edit:"
    while IFS= read -r rel_path; do
        [[ -z "$rel_path" ]] && continue
        echo "   - $rel_path"
    done < <(get_checkpoint_files "$cp")
}

# ---- Commands --------------------------------------------------------------

cmd_checkpoint() {
    local cp="$1"
    local name
    name=$(get_checkpoint_name "$cp")
    local entries
    entries=$(get_checkpoint_entries "$cp")
    local active_cp

    if [[ -z "$entries" ]]; then
        echo "Error: Checkpoint '$cp' not found. Valid: 1, 2, 3, 4" >&2
        exit 1
    fi
    if ! is_checkpoint_golden "$cp"; then
        echo "Checkpoint $cp is already stripped."
        echo "Use './workshop/workshop.sh solve $cp' to restore first."
        exit 1
    fi
    if active_cp="$(get_active_checkpoint)"; then
        echo "Checkpoint $active_cp is currently active."
        echo "Solve it before stripping another checkpoint:"
        echo "  ./workshop/workshop.sh solve $active_cp"
        echo ""
        print_checkpoint_files "$active_cp"
        exit 1
    fi

    while IFS= read -r entry; do
        local ex_id file marker
        ex_id=$(echo "$entry" | cut -d: -f2)
        file="${PROJECT_DIR}/$(echo "$entry" | cut -d: -f3)"
        marker=$(echo "$entry" | cut -d: -f4)
        strip_exercise "$ex_id" "$file" "$marker"
    done <<< "$entries"

    echo ""
    echo "✏️  Checkpoint $cp: $name"
    echo "   Status: STRIPPED — implement the TODOs and test!"
    echo ""
    print_checkpoint_files "$cp"
    echo ""
    echo "   To restore: ./workshop/workshop.sh solve $cp"
}

cmd_solve() {
    local cp="$1"
    local name
    name=$(get_checkpoint_name "$cp")
    local entries
    entries=$(get_checkpoint_entries "$cp")

    if [[ -z "$entries" ]]; then
        echo "Error: Checkpoint '$cp' not found. Valid: 1, 2, 3, 4" >&2
        exit 1
    fi
    if is_checkpoint_golden "$cp"; then
        echo "Checkpoint $cp is already golden."
        return 0
    fi

    # Collect unique files for this checkpoint and restore each from the saved solution ref.
    local restored_files=""
    while IFS= read -r entry; do
        local rel_path
        rel_path=$(echo "$entry" | cut -d: -f3)
        if [[ "$restored_files" != *"$rel_path"* ]]; then
            restored_files="$restored_files $rel_path"
            restore_file_from_golden "$rel_path"
        fi
    done <<< "$entries"

    echo "✅ Checkpoint $cp: $name — RESTORED"
    echo "   All files for this checkpoint are back to the recorded solution."
}

cmd_reset() {
    echo "Resetting all checkpoints to golden..."
    local any=0
    for cp in 1 2 3 4; do
        if ! is_checkpoint_golden "$cp"; then
            cmd_solve "$cp"
            any=1
        fi
    done
    [[ $any -eq 0 ]] && echo "All checkpoints are already golden."
    echo ""
    echo "Done! Full working solution restored."
}

cmd_status() {
    local active_cp=""
    if active_cp="$(get_active_checkpoint)"; then
        :
    else
        active_cp=""
    fi

    echo ""
    echo "┌──────┬───────────┬────────────────────────────────────────────────┐"
    echo "│  CP  │  Status   │  Name                                          │"
    echo "├──────┼───────────┼────────────────────────────────────────────────┤"
    for cp in 1 2 3 4; do
        local name status
        name=$(get_checkpoint_name "$cp")
        if is_checkpoint_golden "$cp"; then
            status="✅ golden"
        else
            status="✏️  TODO  "
        fi
        printf "│  %-3s │ %s │  %-46s│\n" "$cp" "$status" "$name"
    done
    echo "└──────┴───────────┴────────────────────────────────────────────────┘"
    echo ""
    echo "Commands:"
    echo "  ./workshop/workshop.sh checkpoint N   Strip checkpoint N"
    echo "  ./workshop/workshop.sh solve N        Restore golden for checkpoint N"
    echo "  ./workshop/workshop.sh reset          Restore all to golden"
    echo "  ./workshop/create_scaffold_branch.sh  Create a local scaffold branch"
    echo ""
    if [[ -n "$active_cp" ]]; then
        echo "Active checkpoint: $active_cp ($(get_checkpoint_name "$active_cp"))"
        print_checkpoint_files "$active_cp"
        echo ""
    else
        echo "Active checkpoint: none"
        echo "Use './workshop/workshop.sh checkpoint N' to strip exactly one exercise."
        echo ""
    fi
}

# ---- Main ------------------------------------------------------------------

case "${1:-}" in
    checkpoint|cp)
        [[ -z "${2:-}" ]] && { echo "Usage: $0 checkpoint <1|2|3|4>"; exit 1; }
        cmd_checkpoint "$2"
        ;;
    solve|s)
        [[ -z "${2:-}" ]] && { echo "Usage: $0 solve <1|2|3|4>"; exit 1; }
        cmd_solve "$2"
        ;;
    reset|r)  cmd_reset ;;
    status|st) cmd_status ;;
    *)
        echo "Workshop Checkpoint Script"
        echo ""
        echo "Usage:"
        echo "  $0 checkpoint <N>   Strip checkpoint N"
        echo "  $0 solve <N>        Restore golden for checkpoint N"
        echo "  $0 reset            Restore all to golden"
        echo "  $0 status           Show checkpoint states"
        echo "  ./workshop/create_scaffold_branch.sh  Create a local scaffold branch"
        echo ""
        echo "Checkpoints:"
        echo "  1  Implement a Tool          (search_uploaded_materials)"
        echo "  2  Agent + Handoffs          (CourseMaterialAgent + triage)"
        echo "  3  Structured Output + Prompt (TopicSummary + prompt engineering)"
        echo "  4  MCP Integration           (filesystem server + connection)"
        echo ""
        echo "Example:"
        echo "  $0 cp 1    # Strip checkpoint 1"
        echo "  $0 s 1     # Stuck? Restore golden"
        echo "  $0 cp 2    # Move to next"
        ;;
esac
