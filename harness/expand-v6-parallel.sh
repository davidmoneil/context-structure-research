#!/bin/bash
#
# V6 Expansion - PARALLEL using Claude
# Runs multiple topics simultaneously
#

set -uo pipefail

PROJECT_ROOT="$HOME/Code/context-structure-research"
SOURCE_V6="$PROJECT_ROOT/soong-daystrom/_source-v6"
LOG_DIR="$PROJECT_ROOT/results/v6-parallel"
mkdir -p "$LOG_DIR"

# Function to generate docs for one topic
generate_topic() {
    local TOPIC="$1"
    local DESCRIPTION="$2"
    local LOG_FILE="$LOG_DIR/${TOPIC}.log"

    mkdir -p "$SOURCE_V6/$TOPIC"
    echo "[$TOPIC] Starting at $(date)" > "$LOG_FILE"

    for i in {1..10}; do
        OUTPUT_FILE="$SOURCE_V6/$TOPIC/${TOPIC}-doc-${i}.md"

        # Skip if exists and good size
        if [ -f "$OUTPUT_FILE" ]; then
            existing=$(wc -w < "$OUTPUT_FILE" 2>/dev/null || echo 0)
            if [ "$existing" -gt 2000 ]; then
                echo "  Doc $i: skip (exists $existing words)" >> "$LOG_FILE"
                continue
            fi
        fi

        echo -n "  Doc $i: generating..." >> "$LOG_FILE"

        PROMPT="You are creating internal corporate documentation for Soong-Daystrom Industries, a technology company specializing in AI, robotics, and neural interfaces.

Write a detailed internal document about: $DESCRIPTION

Document $i of 10 in the $TOPIC series.

REQUIREMENTS:
- Write 2500-3000 words
- Use dates between 2120-2125
- Reference executives: Dr. Maya Chen (CEO), Marcus Williams (COO), Dr. James Okonkwo (CTO), Dr. Wei Zhang (Chief Scientist)
- Reference products: PCS-9000 robotics, NIM-7 neural interface, IAP Platform
- Reference projects: Prometheus (AI safety), Atlas (infrastructure), Hermes (logistics)
- Include specific financial figures, percentages, KPIs
- Use markdown with headers, bullet points, tables

Output ONLY the document content."

        claude -p "$PROMPT" --model haiku --output-format text > "$OUTPUT_FILE" 2>/dev/null

        if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
            words=$(wc -w < "$OUTPUT_FILE")
            echo " $words words" >> "$LOG_FILE"
        else
            echo " FAILED" >> "$LOG_FILE"
            rm -f "$OUTPUT_FILE"
        fi
    done

    echo "[$TOPIC] Complete at $(date)" >> "$LOG_FILE"
}

export -f generate_topic
export SOURCE_V6 LOG_DIR

echo "=== V6 Parallel Expansion ===" | tee "$LOG_DIR/main.log"
echo "Start: $(date)" | tee -a "$LOG_DIR/main.log"
echo "Current words: $(find "$SOURCE_V6" -name "*.md" -exec cat {} + 2>/dev/null | wc -w)" | tee -a "$LOG_DIR/main.log"
echo "" | tee -a "$LOG_DIR/main.log"

# Launch all topics in parallel
echo "Launching parallel topic generators..." | tee -a "$LOG_DIR/main.log"

generate_topic "strategic-planning" "Comprehensive five-year strategic planning including market analysis, growth projections, competitive positioning" &
generate_topic "rd-quarterly" "Quarterly R&D progress reports with experiment results, prototype testing, breakthrough discoveries" &
generate_topic "financial-analysis" "Deep financial analysis with cash flow projections, capital expenditure plans, profitability metrics" &
generate_topic "customer-implementations" "Customer implementation case studies with technical details, ROI metrics, deployment timelines" &
generate_topic "engineering-specs" "Engineering specifications, system architecture documents, API documentation, technical design reviews" &

# Wait for first batch
wait
echo "Batch 1 complete at $(date)" | tee -a "$LOG_DIR/main.log"

generate_topic "manufacturing-ops" "Manufacturing process documentation, quality control procedures, supply chain logistics" &
generate_topic "talent-development" "Employee development programs, training curricula, leadership pipelines" &
generate_topic "regulatory-compliance" "Legal compliance frameworks, regulatory filings, audit reports, risk assessment" &
generate_topic "market-intelligence" "Market research reports, competitive intelligence briefs, customer segmentation analysis" &
generate_topic "operations-excellence" "Operations improvement initiatives, efficiency metrics, process optimization reports" &

# Wait for second batch
wait
echo "Batch 2 complete at $(date)" | tee -a "$LOG_DIR/main.log"

# Final count
FINAL=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + 2>/dev/null | wc -w)
echo "" | tee -a "$LOG_DIR/main.log"
echo "=== COMPLETE ===" | tee -a "$LOG_DIR/main.log"
echo "Final: $FINAL words" | tee -a "$LOG_DIR/main.log"
echo "End: $(date)" | tee -a "$LOG_DIR/main.log"
