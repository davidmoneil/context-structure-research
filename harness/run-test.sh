#!/bin/bash
#
# Run a single test and capture detailed results
# Designed for manual testing and verification
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
QUESTIONS_FILE="$SCRIPT_DIR/questions.json"
STRUCTURES_DIR="$PROJECT_ROOT/soong-daystrom"
RESULTS_DIR="$PROJECT_ROOT/results/raw"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
Usage: $(basename "$0") --structure <name> --question <id> [OPTIONS]

Run a single test for verification.

OPTIONS:
    --structure <name>    Structure: monolith, flat, shallow, deep, very-deep
    --question <id>       Question ID (e.g., NAV-001)
    --model <name>        Model: haiku (default), sonnet, opus
    --loading <method>    Loading: classic (default), adddir
    --verbose             Show detailed output
    --dry-run             Show what would run without executing

EXAMPLES:
    $(basename "$0") --structure shallow --question NAV-001
    $(basename "$0") --structure deep --question XREF-001 --model sonnet
    $(basename "$0") --structure flat --question NAV-001 --loading adddir
EOF
}

# Defaults
STRUCTURE=""
QUESTION=""
MODEL="haiku"
LOADING="classic"
VERBOSE=false
DRY_RUN=false
CUSTOM_RESULTS_DIR=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --structure) STRUCTURE="$2"; shift 2 ;;
        --question) QUESTION="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --loading) LOADING="$2"; shift 2 ;;
        --results-dir) CUSTOM_RESULTS_DIR="$2"; shift 2 ;;
        --verbose) VERBOSE=true; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Override RESULTS_DIR if custom provided
if [[ -n "$CUSTOM_RESULTS_DIR" ]]; then
    RESULTS_DIR="$CUSTOM_RESULTS_DIR"
fi

if [[ -z "$STRUCTURE" || -z "$QUESTION" ]]; then
    echo "Error: --structure and --question are required"
    usage
    exit 1
fi

# Get model ID
get_model_id() {
    case "$1" in
        haiku)  echo "claude-3-5-haiku-latest" ;;
        sonnet) echo "claude-sonnet-4-20250514" ;;
        opus)   echo "claude-opus-4-20250514" ;;
    esac
}

# Get question details
QUESTION_TEXT=$(jq -r --arg id "$QUESTION" '.[] | select(.id == $id) | .question' "$QUESTIONS_FILE")
QUESTION_TYPE=$(jq -r --arg id "$QUESTION" '.[] | select(.id == $id) | .type' "$QUESTIONS_FILE")
EXPECTED_ANSWER=$(jq -r --arg id "$QUESTION" '.[] | select(.id == $id) | .ground_truth.exact_answer' "$QUESTIONS_FILE")
KEYWORDS=$(jq -r --arg id "$QUESTION" '.[] | select(.id == $id) | .ground_truth.partial_credit_keywords // [] | join(", ")' "$QUESTIONS_FILE")

if [[ -z "$QUESTION_TEXT" || "$QUESTION_TEXT" == "null" ]]; then
    echo -e "${RED}Error: Question not found: $QUESTION${NC}"
    exit 1
fi

# Display test configuration
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Context Structure Research - Single Test Execution${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Structure:  $STRUCTURE"
echo "  Model:      $MODEL"
echo "  Loading:    $LOADING"
echo "  Question:   $QUESTION ($QUESTION_TYPE)"
echo ""
echo -e "${YELLOW}Question:${NC}"
echo "  $QUESTION_TEXT"
echo ""
echo -e "${YELLOW}Expected Answer:${NC}"
echo "  $EXPECTED_ANSWER"
if [[ -n "$KEYWORDS" && "$KEYWORDS" != "null" ]]; then
    echo ""
    echo -e "${YELLOW}Partial Credit Keywords:${NC}"
    echo "  $KEYWORDS"
fi
echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo -e "${YELLOW}[DRY RUN] Would execute test with above configuration${NC}"
    exit 0
fi

# Build the prompt
PROMPT="Answer the following question about Soong-Daystrom Industries based on the provided context. Be concise and specific.

Question: $QUESTION_TEXT

Provide your answer in JSON format:
{\"answer\": \"your answer here\", \"confidence\": \"high|medium|low\", \"sources_used\": [\"list of files you referenced\"]}"

MODEL_ID=$(get_model_id "$MODEL")
STRUCTURE_DIR="$STRUCTURES_DIR/$STRUCTURE"

echo ""
echo -e "${YELLOW}Executing test...${NC}"
echo ""

START_TIME=$(date +%s.%N)

# Execute based on loading method
if [[ "$LOADING" == "classic" ]]; then
    echo "  Mode: Classic (cd into structure directory)"
    echo "  Directory: $STRUCTURE_DIR"
    echo ""

    RESPONSE=$(cd "$STRUCTURE_DIR" && claude -p "$PROMPT" --model "$MODEL_ID" --output-format json 2>&1) || true
else
    echo "  Mode: Add-dir (load from project root)"
    echo "  Add-dir: $STRUCTURE_DIR"
    echo ""

    export CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
    RESPONSE=$(cd "$PROJECT_ROOT" && claude -p "$PROMPT" --model "$MODEL_ID" --add-dir "$STRUCTURE_DIR" --output-format json 2>&1) || true
    unset CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD
fi

END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${YELLOW}Response:${NC}"
echo "$RESPONSE"
echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${YELLOW}Execution Time:${NC} ${DURATION}s"
echo ""

# Try to extract answer from response
EXTRACTED_ANSWER=$(echo "$RESPONSE" | jq -r '.result // .answer // empty' 2>/dev/null || echo "$RESPONSE")

# Simple scoring
echo -e "${YELLOW}Quick Score:${NC}"

# Check for exact match
NORMALIZED_EXPECTED=$(echo "$EXPECTED_ANSWER" | tr '[:upper:]' '[:lower:]')
NORMALIZED_RESPONSE=$(echo "$EXTRACTED_ANSWER" | tr '[:upper:]' '[:lower:]')

if echo "$NORMALIZED_RESPONSE" | grep -qi "$NORMALIZED_EXPECTED"; then
    echo -e "  ${GREEN}✓ Exact/partial match found${NC}"
else
    # Check keywords
    KEYWORD_MATCHES=0
    KEYWORD_COUNT=0
    if [[ -n "$KEYWORDS" && "$KEYWORDS" != "null" ]]; then
        IFS=',' read -ra KW_ARRAY <<< "$KEYWORDS"
        for kw in "${KW_ARRAY[@]}"; do
            kw=$(echo "$kw" | xargs | tr '[:upper:]' '[:lower:]')
            KEYWORD_COUNT=$((KEYWORD_COUNT + 1))
            if echo "$NORMALIZED_RESPONSE" | grep -qi "$kw"; then
                KEYWORD_MATCHES=$((KEYWORD_MATCHES + 1))
            fi
        done
        if [[ $KEYWORD_MATCHES -gt 0 ]]; then
            echo -e "  ${YELLOW}~ Partial match: $KEYWORD_MATCHES/$KEYWORD_COUNT keywords${NC}"
        else
            echo -e "  ${RED}✗ No match found${NC}"
        fi
    else
        echo -e "  ${RED}✗ No exact match found${NC}"
    fi
fi

# Save result
RESULT_FILE="$RESULTS_DIR/$MODEL/${STRUCTURE}_${LOADING}_100_${QUESTION}.json"
mkdir -p "$(dirname "$RESULT_FILE")"

jq -n \
    --arg qid "$QUESTION" \
    --arg question "$QUESTION_TEXT" \
    --arg qtype "$QUESTION_TYPE" \
    --arg structure "$STRUCTURE" \
    --arg model "$MODEL" \
    --arg loading "$LOADING" \
    --arg response "$RESPONSE" \
    --arg expected "$EXPECTED_ANSWER" \
    --arg duration "$DURATION" \
    --arg timestamp "$(date -Iseconds)" \
    '{
        question_id: $qid,
        question: $question,
        question_type: $qtype,
        config: {
            structure: $structure,
            model: $model,
            loading_method: $loading,
            load_percent: 100
        },
        response: $response,
        expected_answer: $expected,
        metadata: {
            duration_seconds: ($duration | tonumber),
            timestamp: $timestamp
        }
    }' > "$RESULT_FILE"

echo ""
echo -e "${GREEN}Result saved to:${NC} $RESULT_FILE"
echo ""
