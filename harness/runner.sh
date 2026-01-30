#!/bin/bash
#
# Context Structure Research - Test Runner
# Executes Claude Code tests across structure variants and loading methods
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
QUESTIONS_FILE="$SCRIPT_DIR/questions.json"
RESULTS_DIR="$PROJECT_ROOT/results/raw"
STRUCTURES_DIR="$PROJECT_ROOT/soong-daystrom"

# Defaults
STRUCTURE=""
MODEL="haiku"
LOADING="classic"
QUESTION=""
LOAD_PERCENT="100"
DRY_RUN=false
VERBOSE=false
RUN_ALL=false

# Valid options
VALID_STRUCTURES=("monolith" "flat" "shallow" "deep" "very-deep")
VALID_MODELS=("haiku" "sonnet" "opus")
VALID_LOADING=("classic" "adddir")

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Run Claude Code tests for context structure research.

OPTIONS:
    --structure <name>    Structure variant: monolith, flat, shallow, deep, very-deep
    --model <name>        Model to use: haiku (default), sonnet, opus
    --loading <method>    Loading method: classic (default), adddir
    --question <id>       Question ID (e.g., NAV-001) or "all"
    --load <percent>      Context load percentage: 40, 60, 80, 100 (default)
    --all                 Run full test matrix
    --dry-run             Show what would run without executing
    --verbose             Show detailed output
    -h, --help            Show this help

EXAMPLES:
    # Single test
    $(basename "$0") --structure shallow --model haiku --question NAV-001

    # Compare loading methods
    $(basename "$0") --structure deep --loading classic --question XREF-001
    $(basename "$0") --structure deep --loading adddir --question XREF-001

    # Run all questions for one configuration
    $(basename "$0") --structure shallow --model sonnet --question all

    # Full test matrix (warning: expensive!)
    $(basename "$0") --all
EOF
}

log() {
    if [[ "$VERBOSE" == true ]]; then
        echo "[$(date '+%H:%M:%S')] $*" >&2
    fi
}

error() {
    echo "ERROR: $*" >&2
    exit 1
}

validate_structure() {
    local struct="$1"
    for valid in "${VALID_STRUCTURES[@]}"; do
        [[ "$struct" == "$valid" ]] && return 0
    done
    error "Invalid structure: $struct. Valid: ${VALID_STRUCTURES[*]}"
}

validate_model() {
    local model="$1"
    for valid in "${VALID_MODELS[@]}"; do
        [[ "$model" == "$valid" ]] && return 0
    done
    error "Invalid model: $model. Valid: ${VALID_MODELS[*]}"
}

validate_loading() {
    local loading="$1"
    for valid in "${VALID_LOADING[@]}"; do
        [[ "$loading" == "$valid" ]] && return 0
    done
    error "Invalid loading method: $loading. Valid: ${VALID_LOADING[*]}"
}

get_model_id() {
    local model="$1"
    case "$model" in
        haiku)  echo "claude-3-5-haiku-latest" ;;
        sonnet) echo "claude-sonnet-4-20250514" ;;
        opus)   echo "claude-opus-4-20250514" ;;
    esac
}

get_questions() {
    local question_filter="$1"
    if [[ "$question_filter" == "all" ]]; then
        jq -r '.[].id' "$QUESTIONS_FILE"
    else
        echo "$question_filter"
    fi
}

get_question_text() {
    local qid="$1"
    jq -r --arg id "$qid" '.[] | select(.id == $id) | .question' "$QUESTIONS_FILE"
}

run_single_test() {
    local structure="$1"
    local model="$2"
    local loading="$3"
    local question_id="$4"
    local load_pct="$5"

    local question_text
    question_text=$(get_question_text "$question_id")

    if [[ -z "$question_text" ]]; then
        error "Question not found: $question_id"
    fi

    local model_id
    model_id=$(get_model_id "$model")

    local structure_dir="$STRUCTURES_DIR/$structure"
    local output_dir="$RESULTS_DIR/$model"
    local output_file="$output_dir/${structure}_${loading}_${load_pct}_${question_id}.json"

    mkdir -p "$output_dir"

    log "Running: structure=$structure, model=$model, loading=$loading, question=$question_id"

    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY RUN] Would execute:"
        echo "  Structure: $structure"
        echo "  Model: $model_id"
        echo "  Loading: $loading"
        echo "  Question: $question_text"
        echo "  Output: $output_file"
        return 0
    fi

    local start_time
    start_time=$(date +%s.%N)

    local response
    local exit_code=0

    # Build the prompt
    local prompt="Answer the following question about Soong-Daystrom Industries based on the provided context. Be concise and specific.

Question: $question_text

Provide your answer in the following JSON format:
{\"answer\": \"your answer here\", \"confidence\": \"high|medium|low\", \"sources_used\": [\"list of files you referenced\"]}"

    if [[ "$loading" == "classic" ]]; then
        # Classic mode: cd into structure directory
        response=$(cd "$structure_dir" && claude -p "$prompt" --model "$model_id" --output-format json 2>&1) || exit_code=$?
    else
        # Add-dir mode: run from project root with --add-dir
        export CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
        response=$(claude -p "$prompt" --model "$model_id" --add-dir "$structure_dir" --output-format json 2>&1) || exit_code=$?
        unset CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD
    fi

    local end_time
    end_time=$(date +%s.%N)
    local duration
    duration=$(echo "$end_time - $start_time" | bc)

    # Build result JSON
    local result
    result=$(jq -n \
        --arg qid "$question_id" \
        --arg question "$question_text" \
        --arg structure "$structure" \
        --arg model "$model" \
        --arg loading "$loading" \
        --arg load_pct "$load_pct" \
        --arg response "$response" \
        --arg duration "$duration" \
        --arg exit_code "$exit_code" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            question_id: $qid,
            question: $question,
            config: {
                structure: $structure,
                model: $model,
                loading_method: $loading,
                load_percent: ($load_pct | tonumber)
            },
            response: $response,
            metadata: {
                duration_seconds: ($duration | tonumber),
                exit_code: ($exit_code | tonumber),
                timestamp: $timestamp
            }
        }')

    echo "$result" > "$output_file"

    if [[ "$VERBOSE" == true ]]; then
        echo "Result saved to: $output_file"
        echo "Duration: ${duration}s"
    fi

    # Brief summary
    echo "[OK] $structure/$loading/$question_id (${duration}s)"
}

run_full_matrix() {
    local total=0
    local completed=0

    # Calculate total tests
    for structure in "${VALID_STRUCTURES[@]}"; do
        for model in "${VALID_MODELS[@]}"; do
            for loading in "${VALID_LOADING[@]}"; do
                local question_count
                question_count=$(jq '. | length' "$QUESTIONS_FILE")
                total=$((total + question_count))
            done
        done
    done

    echo "Full test matrix: $total tests"
    echo "Structures: ${VALID_STRUCTURES[*]}"
    echo "Models: ${VALID_MODELS[*]}"
    echo "Loading methods: ${VALID_LOADING[*]}"
    echo ""

    if [[ "$DRY_RUN" != true ]]; then
        read -p "This will be expensive. Continue? (y/N) " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
    fi

    for structure in "${VALID_STRUCTURES[@]}"; do
        for model in "${VALID_MODELS[@]}"; do
            for loading in "${VALID_LOADING[@]}"; do
                while IFS= read -r qid; do
                    run_single_test "$structure" "$model" "$loading" "$qid" "$LOAD_PERCENT"
                    completed=$((completed + 1))
                    echo "Progress: $completed/$total"
                done < <(get_questions "all")
            done
        done
    done

    echo ""
    echo "Complete! Results in: $RESULTS_DIR"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --structure)
            STRUCTURE="$2"
            validate_structure "$STRUCTURE"
            shift 2
            ;;
        --model)
            MODEL="$2"
            validate_model "$MODEL"
            shift 2
            ;;
        --loading)
            LOADING="$2"
            validate_loading "$LOADING"
            shift 2
            ;;
        --question)
            QUESTION="$2"
            shift 2
            ;;
        --load)
            LOAD_PERCENT="$2"
            shift 2
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate requirements
if ! command -v claude &> /dev/null; then
    error "claude command not found. Install Claude Code first."
fi

if ! command -v jq &> /dev/null; then
    error "jq command not found. Install jq first."
fi

if [[ ! -f "$QUESTIONS_FILE" ]]; then
    error "Questions file not found: $QUESTIONS_FILE"
fi

# Execute
if [[ "$RUN_ALL" == true ]]; then
    run_full_matrix
elif [[ -n "$STRUCTURE" && -n "$QUESTION" ]]; then
    if [[ "$QUESTION" == "all" ]]; then
        while IFS= read -r qid; do
            run_single_test "$STRUCTURE" "$MODEL" "$LOADING" "$qid" "$LOAD_PERCENT"
        done < <(get_questions "all")
    else
        run_single_test "$STRUCTURE" "$MODEL" "$LOADING" "$QUESTION" "$LOAD_PERCENT"
    fi
else
    echo "Error: Must specify --structure and --question, or use --all"
    echo ""
    usage
    exit 1
fi
