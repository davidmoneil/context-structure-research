#!/bin/bash
# Build V5.5 enhancement structures using Claude
# V5.5 = 2-sentence summary + 10 keywords (combining best of V5.1 and V5.3)

set -e
cd ~/Code/context-structure-research

LOG_DIR="results/v5.5-build"
mkdir -p "$LOG_DIR"

echo "=== Building V5.5 (2-sentence + keywords) with Claude ==="
echo "Start: $(date)"
echo ""

generate_index_entry() {
    local FILE="$1"
    local RELPATH="$2"

    CONTENT=$(head -c 8000 "$FILE")

    # Use Claude to generate summary + keywords
    claude --model haiku --print "For this document, provide:
1. A 2-sentence summary capturing the most important specific facts (names, dates, numbers, key decisions)
2. Exactly 10 keywords that would help find this document (include proper nouns, product names, dates, technical terms)

Document content:
$CONTENT

Format your response EXACTLY as:
**Summary**: [Your 2 sentences here]
**Keywords**: [keyword1, keyword2, keyword3, keyword4, keyword5, keyword6, keyword7, keyword8, keyword9, keyword10]" 2>/dev/null
}

process_structure() {
    local STRUCTURE="$1"
    local SOURCE_DIR="soong-daystrom/$STRUCTURE"
    local TARGET_DIR="soong-daystrom/${STRUCTURE}-v5.5"
    local INDEX_FILE="$TARGET_DIR/_index.md"
    local LOG_FILE="$LOG_DIR/${STRUCTURE}.log"

    echo "[$STRUCTURE] Starting..." | tee "$LOG_FILE"

    # Copy structure
    rm -rf "$TARGET_DIR"
    cp -r "$SOURCE_DIR" "$TARGET_DIR"

    # Create index header
    cat > "$INDEX_FILE" << 'HEADER'
# Content Index

This index provides brief summaries and keywords for all documents.
Use @ references to include relevant documents based on their summaries.

---

HEADER

    # Get all files
    FILES=$(find "$TARGET_DIR" -name "*.md" ! -name "_index.md" | sort)
    TOTAL=$(echo "$FILES" | wc -l)
    COUNT=0

    # Process files (3 at a time for parallel speedup)
    for file in $FILES; do
        RELPATH="${file#$TARGET_DIR/}"
        COUNT=$((COUNT + 1))

        echo "  [$COUNT/$TOTAL] $RELPATH" | tee -a "$LOG_FILE"

        # Generate entry
        ENTRY=$(generate_index_entry "$file" "$RELPATH")

        if [ -n "$ENTRY" ]; then
            echo "" >> "$INDEX_FILE"
            echo "## @$RELPATH" >> "$INDEX_FILE"
            echo "$ENTRY" >> "$INDEX_FILE"
        fi
    done

    WORDS=$(wc -w < "$INDEX_FILE")
    echo "[$STRUCTURE] Complete - $WORDS words in index" | tee -a "$LOG_FILE"
}

# Run both structures in parallel
process_structure "flat-v5" &
PID1=$!

process_structure "deep-v5" &
PID2=$!

# Wait for completion
wait $PID1
wait $PID2

echo ""
echo "=== V5.5 Build Complete ==="
echo "End: $(date)"
