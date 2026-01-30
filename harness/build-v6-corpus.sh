#!/bin/bash
#
# Build V6 corpus (600K words) by expanding V5 content
# Uses Ollama for content generation
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_V5="$PROJECT_ROOT/soong-daystrom/_source-v5"
SOURCE_V6="$PROJECT_ROOT/soong-daystrom/_source-v6"
LOG_FILE="$PROJECT_ROOT/results/v6-build.log"

MODEL="llama3.2"  # Fast local model

echo "=== Building V6 Corpus (Target: 600K words) ===" | tee "$LOG_FILE"
echo "Start: $(date)" | tee -a "$LOG_FILE"

# Create V6 directory
mkdir -p "$SOURCE_V6"
cp -r "$SOURCE_V5"/* "$SOURCE_V6/"

# Count current words
CURRENT_WORDS=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
TARGET_WORDS=600000
NEEDED=$((TARGET_WORDS - CURRENT_WORDS))

echo "Current: $CURRENT_WORDS words" | tee -a "$LOG_FILE"
echo "Target: $TARGET_WORDS words" | tee -a "$LOG_FILE"
echo "Need to add: $NEEDED words" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Topics to expand with new content
EXPANSION_TOPICS=(
    "partnerships:Strategic partnerships and joint ventures"
    "supply-chain:Supply chain and manufacturing operations"
    "patents:Patent portfolio and intellectual property"
    "sustainability:Environmental sustainability initiatives"
    "training:Employee training and development programs"
    "incidents:Security incidents and crisis management"
    "acquisitions:Additional acquisition targets and due diligence"
    "regional:Regional office operations and expansions"
    "compliance:Regulatory compliance and certifications"
    "innovation:Innovation lab projects and prototypes"
)

# Create new topic directories and generate content
for topic_info in "${EXPANSION_TOPICS[@]}"; do
    TOPIC="${topic_info%%:*}"
    DESCRIPTION="${topic_info#*:}"

    mkdir -p "$SOURCE_V6/$TOPIC"
    echo "Generating content for: $TOPIC" | tee -a "$LOG_FILE"

    # Generate 5 detailed documents per topic (~3000 words each = 30K per topic)
    for i in {1..5}; do
        OUTPUT_FILE="$SOURCE_V6/$TOPIC/${TOPIC}-document-${i}.md"

        if [ -f "$OUTPUT_FILE" ]; then
            echo "  Skipping $OUTPUT_FILE (exists)" | tee -a "$LOG_FILE"
            continue
        fi

        echo "  Generating document $i..." | tee -a "$LOG_FILE"

        PROMPT="You are a corporate document writer for Soong-Daystrom Industries, a fictional technology company specializing in AI, robotics, and neural interfaces.

Write a detailed internal document about: $DESCRIPTION (Part $i of 5)

The document should:
- Be 2500-3500 words
- Include specific dates (2120-2125 timeframe), names, figures, and metrics
- Reference other departments (R&D, Finance, Legal, Operations)
- Include executive names like Dr. Maya Chen (CEO), Marcus Williams (COO), Dr. James Okonkwo (CTO)
- Mention products like PCS-9000, NIM-7, IAP Platform
- Reference projects like Prometheus, Atlas, Hermes
- Use professional corporate tone
- Include section headers in markdown format

Write the complete document now:"

        # Generate with Ollama
        ollama run "$MODEL" "$PROMPT" > "$OUTPUT_FILE" 2>/dev/null || {
            echo "    Failed to generate $OUTPUT_FILE" | tee -a "$LOG_FILE"
            continue
        }

        WORDS=$(wc -w < "$OUTPUT_FILE")
        echo "    Generated: $WORDS words" | tee -a "$LOG_FILE"
    done
done

# Final word count
FINAL_WORDS=$(find "$SOURCE_V6" -name "*.md" -exec cat {} + | wc -w)
echo "" | tee -a "$LOG_FILE"
echo "=== V6 Build Complete ===" | tee -a "$LOG_FILE"
echo "Final word count: $FINAL_WORDS" | tee -a "$LOG_FILE"
echo "End: $(date)" | tee -a "$LOG_FILE"
