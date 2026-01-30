#!/bin/bash
# Expand V6 corpus - Pass 2
# Add more content to reach 600K words

set -uo pipefail

PROJECT_ROOT="$HOME/Code/context-structure-research"
SOURCE_V6="$PROJECT_ROOT/soong-daystrom/_source-v6"
LOG_FILE="$PROJECT_ROOT/results/v6-expand-pass2.log"

MODEL="llama3.2"

CURRENT_WORDS=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
TARGET=600000
NEEDED=$((TARGET - CURRENT_WORDS))

echo "=== V6 Expansion Pass 2 ===" | tee "$LOG_FILE"
echo "Current: $CURRENT_WORDS words" | tee -a "$LOG_FILE"
echo "Need: $NEEDED more words" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# More topics to add
NEW_TOPICS=(
    "international:International operations and global expansion"
    "mergers:Merger discussions and market consolidation"
    "rd-labs:R&D laboratory reports and experiments"
    "legal:Legal proceedings and regulatory filings"
    "hr-policies:HR policies and workforce planning"
    "investors:Investor relations and shareholder communications"
    "product-roadmap:Product roadmap and feature planning"
    "market-research:Market research and competitive intelligence"
    "quality:Quality assurance and testing protocols"
    "crisis:Crisis management and business continuity"
)

for topic_info in "${NEW_TOPICS[@]}"; do
    TOPIC="${topic_info%%:*}"
    DESCRIPTION="${topic_info#*:}"

    mkdir -p "$SOURCE_V6/$TOPIC"
    echo "Generating: $TOPIC" | tee -a "$LOG_FILE"

    for i in {1..5}; do
        OUTPUT_FILE="$SOURCE_V6/$TOPIC/${TOPIC}-doc-${i}.md"
        [ -f "$OUTPUT_FILE" ] && continue

        PROMPT="Write a 2000-word internal corporate document for Soong-Daystrom Industries about: $DESCRIPTION (Part $i).
Include: specific dates (2120-2125), executive names (Dr. Maya Chen CEO, Marcus Williams COO, Dr. James Okonkwo CTO), product names (PCS-9000, NIM-7, IAP), project names (Prometheus, Atlas, Hermes), financial figures, and department references.
Use markdown headers. Be detailed and specific."

        ollama run "$MODEL" "$PROMPT" > "$OUTPUT_FILE" 2>/dev/null
        WORDS=$(wc -w < "$OUTPUT_FILE" 2>/dev/null || echo 0)
        echo "  $TOPIC-doc-$i: $WORDS words" | tee -a "$LOG_FILE"
    done
done

FINAL=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
echo "" | tee -a "$LOG_FILE"
echo "=== Pass 2 Complete ===" | tee -a "$LOG_FILE"
echo "Final: $FINAL words" | tee -a "$LOG_FILE"
