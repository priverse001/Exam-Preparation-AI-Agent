#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SOLUTION_REF_FILE="$SCRIPT_DIR/.solution-ref"
TARGET_BRANCH="${1:-workshop-scaffold}"

require_clean_worktree() {
    if ! git -C "$PROJECT_DIR" diff --quiet || ! git -C "$PROJECT_DIR" diff --cached --quiet; then
        echo "Error: Working tree must be clean before generating a scaffold branch." >&2
        exit 1
    fi

    if [[ -n "$(git -C "$PROJECT_DIR" ls-files --others --exclude-standard)" ]]; then
        echo "Error: Untracked files detected. Clean the repo before generating a scaffold branch." >&2
        exit 1
    fi
}

main() {
    require_clean_worktree

    if git -C "$PROJECT_DIR" show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
        echo "Error: Branch '$TARGET_BRANCH' already exists locally." >&2
        exit 1
    fi

    local source_ref source_branch
    source_ref="$(git -C "$PROJECT_DIR" rev-parse HEAD)"
    source_branch="$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD)"

    git -C "$PROJECT_DIR" switch -c "$TARGET_BRANCH"

    printf '%s\n' "$source_ref" > "$SOLUTION_REF_FILE"

    git -C "$PROJECT_DIR" add -A
    git -C "$PROJECT_DIR" commit -m "$(cat <<EOF
Prepare workshop scaffold branch.

Create a local scaffold branch from ${source_branch} while recording ${source_ref} as the restore source for checkpoint solve/reset commands.
EOF
)"

    echo ""
    echo "Created branch '$TARGET_BRANCH' from $source_branch."
    echo "It starts fully golden so students can run the app end-to-end immediately."
    echo "Use './workshop/workshop.sh checkpoint N' during the workshop to strip one checkpoint at a time."
}

main "$@"
