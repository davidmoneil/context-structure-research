#!/bin/bash
#
# Phase 2: Test Runner
# Iterates strategy folders, runs claude -p from each, captures results.
#
# Usage:
#   ./run-tests.sh                              # Run all non-LLM strategies
#   ./run-tests.sh --dataset soong-v5           # One dataset only
#   ./run-tests.sh --strategy R2.1              # One strategy only
#   ./run-tests.sh --strategy R2.1 --dataset soong-v5 --question NAV-001  # Single test
#   ./run-tests.sh --dry-run                    # Preview without executing
#   ./run-tests.sh --resume                     # Skip existing result files
#   ./run-tests.sh --model sonnet               # Override model
#   ./run-tests.sh --max-tests 5                # Run at most N tests (for pilot runs)

set -euo pipefail

# ─── Nesting Guard ──────────────────────────────────────────────────
# claude -p can't run inside another Claude Code session.
# Unset the marker so nested calls work.
unset CLAUDECODE 2>/dev/null || true

# ─── Context Note ───────────────────────────────────────────────────
# Claude Code walks up the directory tree for .claude/CLAUDE.md files.
# The project root's .claude/CLAUDE.md (~1.5K chars describing the project)
# is loaded for ALL tests. This is a constant across strategies, so it
# doesn't bias relative comparisons. R1 (no strategy CLAUDE.md) still
# gets this root context — it's not truly "zero context" but reflects
# realistic project usage.

# ─── Configuration ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STRATEGIES_DIR="$PROJECT_ROOT/strategies"
RESULTS_DIR="$PROJECT_ROOT/results/phase2/raw"

# Question files per dataset
declare -A QUESTION_FILES=(
    ["soong-v5"]="$PROJECT_ROOT/harness/questions.json"
    ["obsidian"]="$PROJECT_ROOT/test-datasets/obsidian/questions.json"
)

# Model ID mapping
declare -A MODEL_IDS=(
    ["haiku"]="claude-haiku-4-5-20251001"
    ["sonnet"]="claude-sonnet-4-6-20250514"
    ["opus"]="claude-opus-4-6-20250514"
)

# ─── Defaults ───────────────────────────────────────────────────────
FILTER_DATASET=""
FILTER_STRATEGY=""
FILTER_QUESTION=""
MODEL="haiku"
DRY_RUN=false
RESUME=false
VERBOSE=false
MAX_TESTS=0  # 0 = unlimited
DELAY=2      # seconds between tests (rate limiting)
BUDGET=0.50  # max USD per test (safety guard)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m'

# ─── Functions ──────────────────────────────────────────────────────

usage() {
    cat << 'EOF'
Usage: run-tests.sh [OPTIONS]

Phase 2 Test Runner — runs claude -p from each strategy folder.

OPTIONS:
    --dataset <name>      Filter: soong-v5 or obsidian
    --strategy <id>       Filter: R1, R2.1, R2.3, R3, R4, I1, C1, C3, etc.
    --question <id>       Filter: specific question ID (e.g., NAV-001)
    --model <name>        Model: haiku (default), sonnet, opus
    --resume              Skip tests where result file already exists
    --dry-run             Show what would run without executing
    --max-tests <N>       Stop after N tests (for pilot runs)
    --delay <seconds>     Delay between tests (default: 2)
    --budget <usd>        Max spend per test (default: 0.50)
    --verbose             Show detailed output
    -h, --help            Show this help

EXAMPLES:
    # Pilot run: 3 tests to verify pipeline
    ./run-tests.sh --strategy R1 --dataset soong-v5 --max-tests 3

    # Full run for one strategy
    ./run-tests.sh --strategy R2.1 --resume

    # Full matrix
    ./run-tests.sh --resume
EOF
}

log() {
    echo -e "${DIM}[$(date '+%H:%M:%S')]${NC} $*" >&2
}

error() {
    echo -e "${RED}ERROR:${NC} $*" >&2
    exit 1
}

get_question_ids() {
    local questions_file="$1"
    local filter="$2"
    if [[ -n "$filter" ]]; then
        echo "$filter"
    else
        jq -r '.[].id' "$questions_file"
    fi
}

get_question_text() {
    local questions_file="$1"
    local qid="$2"
    jq -r --arg id "$qid" '.[] | select(.id == $id) | .question' "$questions_file"
}

result_path() {
    local strategy="$1"
    local dataset="$2"
    local question_id="$3"
    echo "$RESULTS_DIR/${strategy}/${dataset}/${question_id}.json"
}

run_single_test() {
    local strategy="$1"
    local dataset="$2"
    local question_id="$3"
    local strategy_dir="$STRATEGIES_DIR/$dataset/$strategy"
    local questions_file="${QUESTION_FILES[$dataset]}"
    local output_file
    output_file=$(result_path "$strategy" "$dataset" "$question_id")

    # Resume: skip if result exists
    if [[ "$RESUME" == true && -f "$output_file" ]]; then
        if [[ "$VERBOSE" == true ]]; then
            log "SKIP $strategy/$dataset/$question_id (result exists)"
        fi
        return 1  # return 1 = skipped
    fi

    local question_text
    question_text=$(get_question_text "$questions_file" "$question_id")
    if [[ -z "$question_text" || "$question_text" == "null" ]]; then
        log "${RED}SKIP${NC} $strategy/$dataset/$question_id (question not found)"
        return 1
    fi

    local model_id="${MODEL_IDS[$MODEL]}"

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "  ${DIM}[DRY]${NC} $strategy/$dataset/$question_id"
        return 1  # don't count as executed
    fi

    # Build the prompt
    local prompt
    prompt="Answer the following question based on the files and context available to you. Be concise and specific.

Question: $question_text

Provide your answer in JSON format:
{\"answer\": \"your concise answer\", \"confidence\": \"high|medium|low\", \"sources_used\": [\"file paths you referenced\"]}"

    # Execute: cd to strategy folder, run claude -p
    local start_time
    start_time=$(date +%s%N)

    local claude_output
    local exit_code=0
    # Redirect stdin from /dev/null so claude doesn't consume the question list pipe
    claude_output=$(cd "$strategy_dir" && claude -p "$prompt" --model "$model_id" --output-format json --max-budget-usd "$BUDGET" --permission-mode bypassPermissions </dev/null 2>&1) || exit_code=$?

    local end_time
    end_time=$(date +%s%N)
    local duration_ms=$(( (end_time - start_time) / 1000000 ))

    # Parse claude JSON output
    local response_text=""
    local cost_usd="null"
    local input_tokens="null"
    local output_tokens="null"
    local cache_read="null"
    local cache_creation="null"
    local num_turns="null"
    local session_id="null"

    if echo "$claude_output" | jq -e '.result' &>/dev/null; then
        response_text=$(echo "$claude_output" | jq -r '.result // ""')
        cost_usd=$(echo "$claude_output" | jq '.total_cost_usd // .cost_usd // null')
        input_tokens=$(echo "$claude_output" | jq '.usage.input_tokens // null')
        output_tokens=$(echo "$claude_output" | jq '.usage.output_tokens // null')
        cache_read=$(echo "$claude_output" | jq '.usage.cache_read_input_tokens // null')
        cache_creation=$(echo "$claude_output" | jq '.usage.cache_creation_input_tokens // null')
        num_turns=$(echo "$claude_output" | jq '.num_turns // null')
        session_id=$(echo "$claude_output" | jq -r '.session_id // "unknown"')
    else
        # Fallback: treat entire output as response text
        response_text="$claude_output"
    fi

    # Write result JSON
    mkdir -p "$(dirname "$output_file")"

    jq -n \
        --arg test_id "phase2-${strategy}-${dataset}-${question_id}" \
        --arg strategy "$strategy" \
        --arg dataset "$dataset" \
        --arg question_id "$question_id" \
        --arg question_text "$question_text" \
        --arg model "$MODEL" \
        --arg model_id "$model_id" \
        --arg response "$response_text" \
        --arg raw_output "$claude_output" \
        --argjson cost_usd "$cost_usd" \
        --argjson input_tokens "$input_tokens" \
        --argjson output_tokens "$output_tokens" \
        --argjson cache_read "$cache_read" \
        --argjson cache_creation "$cache_creation" \
        --argjson num_turns "$num_turns" \
        --argjson duration_ms "$duration_ms" \
        --argjson exit_code "$exit_code" \
        --arg session_id "$session_id" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            test_id: $test_id,
            metadata: {
                phase: "2",
                strategy: $strategy,
                dataset: $dataset,
                question_id: $question_id,
                model: $model,
                model_id: $model_id,
                timestamp: $timestamp,
                session_id: $session_id
            },
            question: $question_text,
            response: $response,
            cost: {
                input_tokens: $input_tokens,
                output_tokens: $output_tokens,
                cache_read_input_tokens: $cache_read,
                cache_creation_input_tokens: $cache_creation,
                total_cost_usd: $cost_usd
            },
            performance: {
                wall_clock_ms: $duration_ms,
                num_turns: $num_turns
            },
            raw_output: $raw_output,
            exit_code: $exit_code
        }' > "$output_file"

    return 0  # return 0 = executed
}

# ─── Parse Arguments ────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dataset)    FILTER_DATASET="$2"; shift 2 ;;
        --strategy)   FILTER_STRATEGY="$2"; shift 2 ;;
        --question)   FILTER_QUESTION="$2"; shift 2 ;;
        --model)      MODEL="$2"; shift 2 ;;
        --resume)     RESUME=true; shift ;;
        --dry-run)    DRY_RUN=true; shift ;;
        --max-tests)  MAX_TESTS="$2"; shift 2 ;;
        --delay)      DELAY="$2"; shift 2 ;;
        --budget)     BUDGET="$2"; shift 2 ;;
        --verbose)    VERBOSE=true; shift ;;
        -h|--help)    usage; exit 0 ;;
        *)            error "Unknown option: $1" ;;
    esac
done

# ─── Validate ───────────────────────────────────────────────────────

if [[ ! -d "$STRATEGIES_DIR" ]]; then
    error "Strategies directory not found: $STRATEGIES_DIR"
fi

if ! command -v jq &>/dev/null; then
    error "jq is required but not found"
fi

if [[ -n "$FILTER_DATASET" && -z "${QUESTION_FILES[$FILTER_DATASET]+x}" ]]; then
    error "Unknown dataset: $FILTER_DATASET. Valid: ${!QUESTION_FILES[*]}"
fi

if [[ -z "${MODEL_IDS[$MODEL]+x}" ]]; then
    error "Unknown model: $MODEL. Valid: ${!MODEL_IDS[*]}"
fi

# ─── Discover Tests ─────────────────────────────────────────────────

# Build list of (strategy, dataset) pairs from existing folders
declare -a TEST_PAIRS=()

for dataset_dir in "$STRATEGIES_DIR"/*/; do
    dataset=$(basename "$dataset_dir")

    # Filter by dataset
    if [[ -n "$FILTER_DATASET" && "$dataset" != "$FILTER_DATASET" ]]; then
        continue
    fi

    # Must have a questions file
    if [[ -z "${QUESTION_FILES[$dataset]+x}" ]]; then
        log "SKIP dataset $dataset (no questions file)"
        continue
    fi

    for strategy_dir in "$dataset_dir"*/; do
        strategy=$(basename "$strategy_dir")

        # Filter by strategy
        if [[ -n "$FILTER_STRATEGY" && "$strategy" != "$FILTER_STRATEGY" ]]; then
            continue
        fi

        # Must have a data symlink
        if [[ ! -L "$strategy_dir/data" && ! -d "$strategy_dir/data" ]]; then
            log "SKIP $strategy/$dataset (no data directory)"
            continue
        fi

        TEST_PAIRS+=("$strategy|$dataset")
    done
done

if [[ ${#TEST_PAIRS[@]} -eq 0 ]]; then
    error "No strategy folders matched filters"
fi

# Count total tests
total_tests=0
for pair in "${TEST_PAIRS[@]}"; do
    IFS='|' read -r strategy dataset <<< "$pair"
    questions_file="${QUESTION_FILES[$dataset]}"
    if [[ -n "$FILTER_QUESTION" ]]; then
        total_tests=$((total_tests + 1))
    else
        q_count=$(jq '. | length' "$questions_file")
        total_tests=$((total_tests + q_count))
    fi
done

# ─── Execute ────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Phase 2: Context Strategy Test Runner${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Model:      $MODEL (${MODEL_IDS[$MODEL]})"
echo "  Strategies: ${#TEST_PAIRS[@]} (strategy × dataset combinations)"
echo "  Tests:      $total_tests total"
[[ $MAX_TESTS -gt 0 ]] && echo "  Max tests:  $MAX_TESTS"
[[ "$RESUME" == true ]] && echo "  Resume:     enabled (skipping existing results)"
[[ "$DRY_RUN" == true ]] && echo "  Mode:       DRY RUN"
echo "  Results:    $RESULTS_DIR/"
echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

executed=0
skipped=0
errors=0
start_time_global=$(date +%s)

for pair in "${TEST_PAIRS[@]}"; do
    IFS='|' read -r strategy dataset <<< "$pair"
    questions_file="${QUESTION_FILES[$dataset]}"

    echo ""
    echo -e "${YELLOW}▸ $strategy / $dataset${NC}"

    while IFS= read -r qid; do
        # Max tests check
        if [[ $MAX_TESTS -gt 0 && $executed -ge $MAX_TESTS ]]; then
            echo ""
            echo -e "${YELLOW}Reached --max-tests limit ($MAX_TESTS)${NC}"
            break 2
        fi

        if run_single_test "$strategy" "$dataset" "$qid"; then
            executed=$((executed + 1))

            # Brief status line
            echo -e "  ${GREEN}✓${NC} $qid ($((executed))/${total_tests})"

            # Rate limiting delay
            if [[ "$DRY_RUN" != true && $DELAY -gt 0 ]]; then
                sleep "$DELAY"
            fi
        else
            skipped=$((skipped + 1))
        fi

    done < <(get_question_ids "$questions_file" "$FILTER_QUESTION")
done

# ─── Summary ────────────────────────────────────────────────────────

end_time_global=$(date +%s)
elapsed=$((end_time_global - start_time_global))

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo "  Executed:  $executed"
echo "  Skipped:   $skipped"
echo "  Errors:    $errors"
echo "  Duration:  ${elapsed}s"
echo "  Results:   $RESULTS_DIR/"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Write run manifest
manifest_file="$RESULTS_DIR/run-$(date +%Y%m%d-%H%M%S).json"
mkdir -p "$RESULTS_DIR"
jq -n \
    --argjson executed "$executed" \
    --argjson skipped "$skipped" \
    --argjson errors "$errors" \
    --argjson elapsed "$elapsed" \
    --argjson total "$total_tests" \
    --arg model "$MODEL" \
    --arg timestamp "$(date -Iseconds)" \
    --arg filter_dataset "$FILTER_DATASET" \
    --arg filter_strategy "$FILTER_STRATEGY" \
    '{
        run_summary: {
            timestamp: $timestamp,
            model: $model,
            total_possible: $total,
            executed: $executed,
            skipped: $skipped,
            errors: $errors,
            elapsed_seconds: $elapsed,
            filters: {
                dataset: (if $filter_dataset == "" then null else $filter_dataset end),
                strategy: (if $filter_strategy == "" then null else $filter_strategy end)
            }
        }
    }' > "$manifest_file"

echo ""
echo -e "Run manifest: ${DIM}$manifest_file${NC}"
echo ""
