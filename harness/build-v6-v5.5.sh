#!/bin/bash
# Build V6-V5.5 enhancement structures using Claude
# V5.5 = 2-sentence summary + 10 keywords
# V6 = 622K words, 277 files

set -e
cd ~/Code/context-structure-research

LOG_DIR="results/v6-build"
mkdir -p "$LOG_DIR"
TEMP_DIR="$LOG_DIR/temp"
mkdir -p "$TEMP_DIR"

echo "=== Building V6-V5.5 (2-sentence + keywords) with Claude ===" | tee "$LOG_DIR/main.log"
echo "Start: $(date)" | tee -a "$LOG_DIR/main.log"

# Maximum parallel processes
MAX_PARALLEL=8

generate_single_entry() {
    local FILE="$1"
    local OUTPUT="$2"
    local RELPATH="$3"

    CONTENT=$(head -c 8000 "$FILE")

    RESULT=$(claude --model haiku --print "For this document, provide:
1. A 2-sentence summary capturing the most important specific facts (names, dates, numbers, key decisions)
2. Exactly 10 keywords that would help find this document (include proper nouns, product names, dates, technical terms)

Document:
$CONTENT

Format EXACTLY as:
**Summary**: [2 sentences]
**Keywords**: [10 comma-separated keywords]" 2>/dev/null)

    if [ -n "$RESULT" ]; then
        echo "" > "$OUTPUT"
        echo "## @$RELPATH" >> "$OUTPUT"
        echo "$RESULT" >> "$OUTPUT"
    fi
}

process_structure() {
    local STRUCTURE="$1"
    local SOURCE_DIR="soong-daystrom/$STRUCTURE"
    local TARGET_DIR="soong-daystrom/${STRUCTURE}-v5.5"
    local INDEX_FILE="$TARGET_DIR/_index.md"
    local LOG_FILE="$LOG_DIR/${STRUCTURE}.log"
    local STRUCT_TEMP="$TEMP_DIR/$STRUCTURE"

    mkdir -p "$STRUCT_TEMP"

    echo "[$STRUCTURE] Starting at $(date)" > "$LOG_FILE"

    # Copy structure
    rm -rf "$TARGET_DIR"
    cp -r "$SOURCE_DIR" "$TARGET_DIR"

    # Create index header
    cat > "$INDEX_FILE" << 'HEADER'
# Content Index (V6-V5.5)

This index provides brief summaries and keywords for all documents.
Use @ references to include relevant documents based on their summaries.

---
HEADER

    # Get all files
    mapfile -t FILES < <(find "$TARGET_DIR" -name "*.md" ! -name "_index.md" ! -name "CLAUDE.md" | sort)
    TOTAL=${#FILES[@]}

    echo "  Processing $TOTAL files with $MAX_PARALLEL parallel workers..." >> "$LOG_FILE"
    echo "[$STRUCTURE] Processing $TOTAL files..."

    # Process in parallel batches
    COUNT=0
    RUNNING=0

    for file in "${FILES[@]}"; do
        RELPATH="${file#$TARGET_DIR/}"
        COUNT=$((COUNT + 1))

        # Sanitize filename for temp file
        SAFE_NAME=$(echo "$RELPATH" | tr '/' '_')
        TEMP_FILE="$STRUCT_TEMP/${COUNT}_${SAFE_NAME}.tmp"

        echo "  [$COUNT/$TOTAL] $RELPATH" >> "$LOG_FILE"

        # Progress update every 20 files
        if [ $((COUNT % 20)) -eq 0 ]; then
            echo "[$STRUCTURE] Progress: $COUNT/$TOTAL"
        fi

        # Launch in background
        generate_single_entry "$file" "$TEMP_FILE" "$RELPATH" &

        RUNNING=$((RUNNING + 1))

        # Wait when we hit max parallel
        if [ $RUNNING -ge $MAX_PARALLEL ]; then
            wait -n 2>/dev/null || true
            RUNNING=$((RUNNING - 1))
        fi
    done

    # Wait for remaining
    wait

    # Combine all temp files in order
    for i in $(seq 1 $TOTAL); do
        TEMP_FILES=$(ls "$STRUCT_TEMP/${i}_"*.tmp 2>/dev/null || true)
        for tf in $TEMP_FILES; do
            if [ -f "$tf" ]; then
                cat "$tf" >> "$INDEX_FILE"
            fi
        done
    done

    # Cleanup
    rm -rf "$STRUCT_TEMP"

    WORDS=$(wc -w < "$INDEX_FILE")
    echo "[$STRUCTURE] Complete at $(date) - $WORDS words" >> "$LOG_FILE"
    echo "[$STRUCTURE] Complete - $WORDS words in index"
}

export -f generate_single_entry

# Run both V6 structures
echo "Processing flat-v6 and deep-v6 structures..."

# Run flat-v6 first
process_structure "flat-v6" 2>&1 | tee -a "$LOG_DIR/main.log" &
FLAT_PID=$!

# Small delay to stagger
sleep 2

process_structure "deep-v6" 2>&1 | tee -a "$LOG_DIR/main.log" &
DEEP_PID=$!

# Wait for both
wait $FLAT_PID
wait $DEEP_PID

echo "" | tee -a "$LOG_DIR/main.log"
echo "=== V6-V5.5 Build Complete ===" | tee -a "$LOG_DIR/main.log"
echo "End: $(date)" | tee -a "$LOG_DIR/main.log"

# Show index sizes
echo ""
echo "Index sizes:"
wc -l soong-daystrom/flat-v6-v5.5/_index.md soong-daystrom/deep-v6-v5.5/_index.md 2>/dev/null

echo ""
echo "Structure variants created:"
ls -d soong-daystrom/*-v6* 2>/dev/null
