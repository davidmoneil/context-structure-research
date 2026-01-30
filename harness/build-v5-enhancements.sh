#!/bin/bash
#
# Build V5 enhancement variations (V5.1 - V5.4)
# Creates index files with summaries/keywords for @ reference testing
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_V5="$PROJECT_ROOT/soong-daystrom/_source-v5"
LOG_FILE="$PROJECT_ROOT/results/v5-enhancements-build.log"

MODEL="llama3.2"

# Variants to build
# V5.1 = 2-sentence summaries
# V5.2 = 5-sentence summaries
# V5.3 = 10 keywords
# V5.4 = combined (2-sentence + keywords)

VARIANT="${1:-all}"

echo "=== Building V5 Enhancement Variants ===" | tee "$LOG_FILE"
echo "Start: $(date)" | tee -a "$LOG_FILE"
echo "Variant: $VARIANT" | tee -a "$LOG_FILE"

build_summary_index() {
    local SENTENCES=$1
    local VERSION=$2
    local STRUCTURE=$3  # flat-v5 or deep-v5

    local SOURCE_DIR="$PROJECT_ROOT/soong-daystrom/$STRUCTURE"
    local TARGET_DIR="$PROJECT_ROOT/soong-daystrom/${STRUCTURE}-${VERSION}"
    local INDEX_FILE="$TARGET_DIR/_index.md"

    echo "" | tee -a "$LOG_FILE"
    echo "Building $VERSION for $STRUCTURE ($SENTENCES-sentence summaries)..." | tee -a "$LOG_FILE"

    # Copy structure
    rm -rf "$TARGET_DIR"
    cp -r "$SOURCE_DIR" "$TARGET_DIR"

    # Create index file
    cat > "$INDEX_FILE" << 'HEADER'
# Content Index

This index provides summaries of all documents to help locate relevant information.

---

HEADER

    # Generate summaries for each file
    find "$TARGET_DIR" -name "*.md" ! -name "_index.md" | sort | while read -r file; do
        FILENAME=$(basename "$file")
        RELPATH="${file#$TARGET_DIR/}"

        echo "  Processing: $RELPATH" | tee -a "$LOG_FILE"

        CONTENT=$(head -c 8000 "$file")  # First 8K chars for context

        PROMPT="Summarize this document in exactly $SENTENCES sentences. Be specific - include names, dates, numbers, and key facts.

Document:
$CONTENT

Write exactly $SENTENCES sentences:"

        SUMMARY=$(ollama run "$MODEL" "$PROMPT" 2>/dev/null | head -10)

        if [ -n "$SUMMARY" ]; then
            echo "" >> "$INDEX_FILE"
            echo "## @$RELPATH" >> "$INDEX_FILE"
            echo "$SUMMARY" >> "$INDEX_FILE"
        fi
    done

    echo "  Index created: $INDEX_FILE" | tee -a "$LOG_FILE"
}

build_keyword_index() {
    local VERSION=$1
    local STRUCTURE=$2

    local SOURCE_DIR="$PROJECT_ROOT/soong-daystrom/$STRUCTURE"
    local TARGET_DIR="$PROJECT_ROOT/soong-daystrom/${STRUCTURE}-${VERSION}"
    local INDEX_FILE="$TARGET_DIR/_index.md"

    echo "" | tee -a "$LOG_FILE"
    echo "Building $VERSION for $STRUCTURE (10 keywords)..." | tee -a "$LOG_FILE"

    # Copy structure
    rm -rf "$TARGET_DIR"
    cp -r "$SOURCE_DIR" "$TARGET_DIR"

    # Create index file
    cat > "$INDEX_FILE" << 'HEADER'
# Content Index

This index provides keywords for all documents to help locate relevant information.

---

HEADER

    find "$TARGET_DIR" -name "*.md" ! -name "_index.md" | sort | while read -r file; do
        FILENAME=$(basename "$file")
        RELPATH="${file#$TARGET_DIR/}"

        echo "  Processing: $RELPATH" | tee -a "$LOG_FILE"

        CONTENT=$(head -c 8000 "$file")

        PROMPT="Extract exactly 10 important keywords from this document. Include names, products, dates, and key concepts. Output only the keywords separated by commas.

Document:
$CONTENT

Keywords:"

        KEYWORDS=$(ollama run "$MODEL" "$PROMPT" 2>/dev/null | head -1)

        if [ -n "$KEYWORDS" ]; then
            echo "" >> "$INDEX_FILE"
            echo "## @$RELPATH" >> "$INDEX_FILE"
            echo "**Keywords**: $KEYWORDS" >> "$INDEX_FILE"
        fi
    done

    echo "  Index created: $INDEX_FILE" | tee -a "$LOG_FILE"
}

build_combined_index() {
    local VERSION=$1
    local STRUCTURE=$2

    local SOURCE_DIR="$PROJECT_ROOT/soong-daystrom/$STRUCTURE"
    local TARGET_DIR="$PROJECT_ROOT/soong-daystrom/${STRUCTURE}-${VERSION}"
    local INDEX_FILE="$TARGET_DIR/_index.md"

    echo "" | tee -a "$LOG_FILE"
    echo "Building $VERSION for $STRUCTURE (2-sentence + keywords)..." | tee -a "$LOG_FILE"

    # Copy structure
    rm -rf "$TARGET_DIR"
    cp -r "$SOURCE_DIR" "$TARGET_DIR"

    # Create index file
    cat > "$INDEX_FILE" << 'HEADER'
# Content Index

This index provides summaries and keywords for all documents.

---

HEADER

    find "$TARGET_DIR" -name "*.md" ! -name "_index.md" | sort | while read -r file; do
        FILENAME=$(basename "$file")
        RELPATH="${file#$TARGET_DIR/}"

        echo "  Processing: $RELPATH" | tee -a "$LOG_FILE"

        CONTENT=$(head -c 8000 "$file")

        PROMPT="For this document, provide:
1. A 2-sentence summary with specific facts
2. 10 important keywords (names, products, dates, concepts)

Document:
$CONTENT

Format your response as:
Summary: [2 sentences]
Keywords: [comma-separated list]"

        RESPONSE=$(ollama run "$MODEL" "$PROMPT" 2>/dev/null | head -5)

        if [ -n "$RESPONSE" ]; then
            echo "" >> "$INDEX_FILE"
            echo "## @$RELPATH" >> "$INDEX_FILE"
            echo "$RESPONSE" >> "$INDEX_FILE"
        fi
    done

    echo "  Index created: $INDEX_FILE" | tee -a "$LOG_FILE"
}

# Build requested variants
case "$VARIANT" in
    v5.1|all)
        build_summary_index 2 "v5.1" "flat-v5"
        build_summary_index 2 "v5.1" "deep-v5"
        ;;&
    v5.2|all)
        build_summary_index 5 "v5.2" "flat-v5"
        build_summary_index 5 "v5.2" "deep-v5"
        ;;&
    v5.3|all)
        build_keyword_index "v5.3" "flat-v5"
        build_keyword_index "v5.3" "deep-v5"
        ;;&
    v5.4|all)
        build_combined_index "v5.4" "flat-v5"
        build_combined_index "v5.4" "deep-v5"
        ;;
esac

echo "" | tee -a "$LOG_FILE"
echo "=== V5 Enhancements Complete ===" | tee -a "$LOG_FILE"
echo "End: $(date)" | tee -a "$LOG_FILE"
