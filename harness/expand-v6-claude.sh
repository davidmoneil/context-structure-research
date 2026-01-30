#!/bin/bash
#
# V6 Expansion using Claude API
# Target: 600K words
#

set -uo pipefail

PROJECT_ROOT="$HOME/Code/context-structure-research"
SOURCE_V6="$PROJECT_ROOT/soong-daystrom/_source-v6"
LOG_FILE="$PROJECT_ROOT/results/v6-expand-claude.log"

CURRENT_WORDS=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
TARGET=600000
NEEDED=$((TARGET - CURRENT_WORDS))

echo "=== V6 Expansion (Claude) ===" | tee "$LOG_FILE"
echo "Current: $CURRENT_WORDS words" | tee -a "$LOG_FILE"
echo "Target: $TARGET words" | tee -a "$LOG_FILE"
echo "Need: $NEEDED words" | tee -a "$LOG_FILE"
echo "Start: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Topics with detailed descriptions
TOPICS=(
    "strategic-planning:Comprehensive five-year strategic planning including market analysis, growth projections, competitive positioning, and investment priorities"
    "rd-quarterly:Quarterly R&D progress reports with experiment results, prototype testing, breakthrough discoveries, and patent filings"
    "financial-analysis:Deep financial analysis with cash flow projections, capital expenditure plans, profitability metrics, and investor guidance"
    "customer-implementations:Customer implementation case studies with technical details, ROI metrics, deployment timelines, and lessons learned"
    "engineering-specs:Engineering specifications, system architecture documents, API documentation, and technical design reviews"
    "manufacturing-ops:Manufacturing process documentation, quality control procedures, supply chain logistics, and production optimization"
    "talent-development:Employee development programs, training curricula, leadership pipelines, and organizational development"
    "regulatory-compliance:Legal compliance frameworks, regulatory filings, audit reports, and risk assessment documentation"
    "market-intelligence:Market research reports, competitive intelligence briefs, customer segmentation analysis, and trend forecasts"
    "operations-excellence:Operations improvement initiatives, efficiency metrics, process optimization reports, and continuous improvement programs"
)

DOC_NUM=0
for topic_info in "${TOPICS[@]}"; do
    TOPIC="${topic_info%%:*}"
    DESCRIPTION="${topic_info#*:}"

    mkdir -p "$SOURCE_V6/$TOPIC"
    echo "" | tee -a "$LOG_FILE"
    echo "[$TOPIC]" | tee -a "$LOG_FILE"

    # Generate 10 docs per topic
    for i in {1..10}; do
        OUTPUT_FILE="$SOURCE_V6/$TOPIC/${TOPIC}-doc-${i}.md"

        # Skip if already exists and is long enough
        if [ -f "$OUTPUT_FILE" ]; then
            existing_words=$(wc -w < "$OUTPUT_FILE")
            if [ "$existing_words" -gt 2000 ]; then
                echo "  Skip doc $i (exists: $existing_words words)" | tee -a "$LOG_FILE"
                continue
            fi
        fi

        DOC_NUM=$((DOC_NUM + 1))
        echo -n "  Doc $i..." | tee -a "$LOG_FILE"

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
- Use markdown with headers (##, ###), bullet points, tables
- Make it realistic and detailed

Output ONLY the document content, no preamble."

        # Use Claude CLI with haiku for cost efficiency
        claude -p "$PROMPT" --model haiku --output-format text > "$OUTPUT_FILE" 2>/dev/null

        if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
            WORDS=$(wc -w < "$OUTPUT_FILE")
            echo " $WORDS words" | tee -a "$LOG_FILE"
        else
            echo " FAILED" | tee -a "$LOG_FILE"
            rm -f "$OUTPUT_FILE"
        fi

        # Check progress
        CURRENT=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
        if [ "$CURRENT" -ge "$TARGET" ]; then
            echo "" | tee -a "$LOG_FILE"
            echo "TARGET REACHED: $CURRENT words" | tee -a "$LOG_FILE"
            break 2
        fi
    done
done

FINAL=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
echo "" | tee -a "$LOG_FILE"
echo "=== Complete ===" | tee -a "$LOG_FILE"
echo "Documents generated: $DOC_NUM" | tee -a "$LOG_FILE"
echo "Final: $FINAL words" | tee -a "$LOG_FILE"
echo "End: $(date)" | tee -a "$LOG_FILE"
