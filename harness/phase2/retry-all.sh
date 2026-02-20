#!/bin/bash
# Retry all failed summaries for Sonnet and Gemini
# Safe to set-and-forget overnight
set -e
cd "$(dirname "$0")/../.."

echo "=== Starting retry run: $(date) ==="
echo ""

# Sonnet retries (CLI backend, uses Claude Code subscription)
echo "=== SONNET RETRIES ==="
python3 harness/phase2/generate-summaries.py --model cli:sonnet --retry-failures --dataset obsidian
echo ""
echo "Sonnet obsidian done: $(date)"
echo ""

# Gemini retries (full regenerate, 8s between calls + exponential backoff on 429)
echo "=== GEMINI FULL REGENERATE ==="
echo "Running at ~7.5 RPM (half free tier limit). ETA: ~45 min per dataset."
echo ""
python3 harness/phase2/generate-summaries.py --model gemini:flash --dataset soong-v5
echo ""
echo "Gemini soong-v5 done: $(date)"
echo ""
python3 harness/phase2/generate-summaries.py --model gemini:flash --dataset obsidian
echo ""
echo "Gemini obsidian done: $(date)"

echo ""
echo "=== Final status ==="
for variant in I4-sonnet I4-geminiflash; do
    for ds in soong-v5 obsidian; do
        f="strategies/$ds/$variant/summaries.md"
        if [ -f "$f" ]; then
            c=$(grep -c "Document at " "$f")
            echo "$ds/$variant: $c fallbacks remaining"
        else
            echo "$ds/$variant: NO FILE"
        fi
    done
done
echo ""
echo "=== All done: $(date) ==="
