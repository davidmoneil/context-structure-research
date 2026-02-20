#!/bin/bash
# Search the summary index for files matching keywords.
# Usage: ./search-index.sh keyword1 [keyword2] [keyword3]
# Returns matching summary rows with file paths.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDEX="$SCRIPT_DIR/summaries.md"

if [ $# -eq 0 ]; then
    echo "Usage: ./search-index.sh keyword1 [keyword2] ..."
    echo "Searches summaries.md for files matching the given keywords."
    exit 1
fi

# Build OR pattern from all arguments
PATTERN=$(printf "%s|" "$@")
PATTERN="${PATTERN%|}"  # Remove trailing pipe

grep -iE "$PATTERN" "$INDEX"
