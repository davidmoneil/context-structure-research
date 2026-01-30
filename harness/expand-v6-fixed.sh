#!/bin/bash
#
# V6 Expansion - Fixed version using larger model
# Target: 600K words
#

set -uo pipefail

PROJECT_ROOT="$HOME/Code/context-structure-research"
SOURCE_V6="$PROJECT_ROOT/soong-daystrom/_source-v6"
LOG_FILE="$PROJECT_ROOT/results/v6-expand-fixed.log"

# Use larger model for better instruction following
MODEL="qwen2.5:32b"

CURRENT_WORDS=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
TARGET=600000
NEEDED=$((TARGET - CURRENT_WORDS))
DOCS_NEEDED=$((NEEDED / 2500))  # ~2500 words per doc

echo "=== V6 Expansion (Fixed) ===" | tee "$LOG_FILE"
echo "Model: $MODEL" | tee -a "$LOG_FILE"
echo "Current: $CURRENT_WORDS words" | tee -a "$LOG_FILE"
echo "Target: $TARGET words" | tee -a "$LOG_FILE"
echo "Need: $NEEDED words (~$DOCS_NEEDED docs)" | tee -a "$LOG_FILE"
echo "Start: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Expanded topics - more detailed to get longer content
TOPICS=(
    "strategic-planning:Five-year strategic planning documents including market analysis, growth projections, and competitive positioning for 2125-2130"
    "rd-quarterly:Quarterly R&D progress reports with detailed experiment results, prototype testing, and breakthrough discoveries"
    "financial-deep:Deep financial analysis including cash flow projections, capital expenditure plans, and profitability by product line"
    "customer-success:Customer success stories and case studies with implementation details, ROI metrics, and testimonials"
    "engineering:Engineering specifications, technical architecture documents, and system design reviews"
    "manufacturing:Manufacturing process documentation, quality control procedures, and supply chain optimization"
    "hr-development:Employee development programs, training curricula, and organizational development initiatives"
    "legal-compliance:Legal compliance frameworks, regulatory filings, and risk assessment documentation"
    "marketing-strategy:Marketing strategy documents, campaign analyses, and brand positioning studies"
    "operations:Operations manuals, standard operating procedures, and efficiency improvement reports"
)

DOC_COUNT=0
for topic_info in "${TOPICS[@]}"; do
    TOPIC="${topic_info%%:*}"
    DESCRIPTION="${topic_info#*:}"

    mkdir -p "$SOURCE_V6/$TOPIC"
    echo "[$TOPIC]" | tee -a "$LOG_FILE"

    # Generate 10 docs per topic for more content
    for i in {1..10}; do
        OUTPUT_FILE="$SOURCE_V6/$TOPIC/${TOPIC}-report-${i}.md"

        if [ -f "$OUTPUT_FILE" ]; then
            existing_words=$(wc -w < "$OUTPUT_FILE")
            if [ "$existing_words" -gt 1500 ]; then
                echo "  Skip $i (exists: $existing_words words)" | tee -a "$LOG_FILE"
                continue
            fi
        fi

        echo -n "  Generating doc $i..." | tee -a "$LOG_FILE"

        PROMPT="You are a senior technical writer at Soong-Daystrom Industries, a leading technology company in AI, robotics, and neural interfaces.

Write a comprehensive internal document about: $DESCRIPTION

REQUIREMENTS:
- Length: EXACTLY 2500-3000 words (this is critical - count your words)
- Include specific dates between 2120-2125
- Reference executives: Dr. Maya Chen (CEO), Marcus Williams (COO), Dr. James Okonkwo (CTO), Dr. Wei Zhang (Chief Scientist)
- Reference products: PCS-9000 series, NIM-7 neural interface, IAP Platform
- Reference projects: Project Prometheus (AI safety), Project Atlas (infrastructure), Project Hermes (logistics)
- Include financial figures, percentages, and metrics
- Use markdown formatting with headers (##, ###)
- Include bullet points and tables where appropriate
- Be specific with names, dates, and numbers

This is document $i of 10 in the $TOPIC series. Make it unique and detailed.

Write the complete document now:"

        # Generate with timeout
        timeout 300 ollama run "$MODEL" "$PROMPT" > "$OUTPUT_FILE" 2>/dev/null

        if [ -f "$OUTPUT_FILE" ]; then
            WORDS=$(wc -w < "$OUTPUT_FILE")
            echo " $WORDS words" | tee -a "$LOG_FILE"
            DOC_COUNT=$((DOC_COUNT + 1))
        else
            echo " FAILED" | tee -a "$LOG_FILE"
        fi

        # Check if we've hit target
        CURRENT=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
        if [ "$CURRENT" -ge "$TARGET" ]; then
            echo "" | tee -a "$LOG_FILE"
            echo "Target reached! $CURRENT words" | tee -a "$LOG_FILE"
            break 2
        fi
    done
done

FINAL=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
echo "" | tee -a "$LOG_FILE"
echo "=== Expansion Complete ===" | tee -a "$LOG_FILE"
echo "Documents generated: $DOC_COUNT" | tee -a "$LOG_FILE"
echo "Final word count: $FINAL" | tee -a "$LOG_FILE"
echo "End: $(date)" | tee -a "$LOG_FILE"
