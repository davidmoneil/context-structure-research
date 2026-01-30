#!/bin/bash
# Build missing V6 structure variants: shallow-v6 and very-deep-v6

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$PROJECT_ROOT/soong-daystrom/_source-v6"

echo "================================================"
echo "  Building Missing V6 Structure Variants"
echo "================================================"

# ============================================
# SHALLOW-V6: One level of folders
# ============================================
build_shallow() {
    local TARGET_DIR="$PROJECT_ROOT/soong-daystrom/shallow-v6"

    echo ""
    echo "Building shallow-v6..."

    # Remove if exists
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"

    # Copy CLAUDE.md
    if [ -f "$SOURCE_DIR/CLAUDE.md" ]; then
        cp "$SOURCE_DIR/CLAUDE.md" "$TARGET_DIR/"
    fi

    # Copy all folders (one level deep)
    for dir in "$SOURCE_DIR"/*/; do
        if [ -d "$dir" ]; then
            dir_name=$(basename "$dir")
            mkdir -p "$TARGET_DIR/$dir_name"
            # Copy all .md files from this directory and subdirectories into the one folder
            find "$dir" -name "*.md" -exec cp {} "$TARGET_DIR/$dir_name/" \;
        fi
    done

    local file_count=$(find "$TARGET_DIR" -name "*.md" | wc -l)
    echo "  Created shallow-v6 with $file_count files"
}

# ============================================
# VERY-DEEP-V6: 5+ levels of nesting
# ============================================
build_very_deep() {
    local TARGET_DIR="$PROJECT_ROOT/soong-daystrom/very-deep-v6"

    echo ""
    echo "Building very-deep-v6..."

    # Remove if exists
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"

    # Copy CLAUDE.md to root
    if [ -f "$SOURCE_DIR/CLAUDE.md" ]; then
        cp "$SOURCE_DIR/CLAUDE.md" "$TARGET_DIR/"
    fi

    # Create deep structure: sdi/company/division/department/category/docs/
    local BASE="$TARGET_DIR/sdi/company"

    # Engineering division
    mkdir -p "$BASE/engineering/tech/docs"
    mkdir -p "$BASE/engineering/research/docs"
    mkdir -p "$BASE/engineering/innovation/docs"

    # Background division
    mkdir -p "$BASE/background/history/timeline/docs"
    mkdir -p "$BASE/background/culture/values/docs"

    # Operations division
    mkdir -p "$BASE/operations/manufacturing/processes/docs"
    mkdir -p "$BASE/operations/facilities/locations/docs"
    mkdir -p "$BASE/operations/quality/metrics/docs"

    # Business division
    mkdir -p "$BASE/business/financial/reports/docs"
    mkdir -p "$BASE/business/investor/relations/docs"
    mkdir -p "$BASE/business/legal/contracts/docs"
    mkdir -p "$BASE/business/marketing/campaigns/docs"

    # People division
    mkdir -p "$BASE/people/hr/policies/docs"
    mkdir -p "$BASE/people/employees/leadership/docs"
    mkdir -p "$BASE/people/employees/teams/docs"

    # External division
    mkdir -p "$BASE/external/partners/integrations/docs"
    mkdir -p "$BASE/external/customers/implementations/docs"
    mkdir -p "$BASE/external/competitors/analysis/docs"
    mkdir -p "$BASE/external/community/outreach/docs"

    # Projects division
    mkdir -p "$BASE/projects/atlas/documentation/docs"
    mkdir -p "$BASE/projects/aria/documentation/docs"
    mkdir -p "$BASE/projects/hermes/documentation/docs"
    mkdir -p "$BASE/projects/prometheus/documentation/docs"

    # Governance division
    mkdir -p "$BASE/governance/compliance/regulations/docs"
    mkdir -p "$BASE/governance/policies/standards/docs"
    mkdir -p "$BASE/governance/meetings/board/docs"

    # Map source directories to deep structure
    declare -A DIR_MAP=(
        ["engineering-specs"]="engineering/tech/docs"
        ["innovation"]="engineering/innovation/docs"
        ["research"]="engineering/research/docs"
        ["history"]="background/history/timeline/docs"
        ["manufacturing-ops"]="operations/manufacturing/processes/docs"
        ["facilities"]="operations/facilities/locations/docs"
        ["operations"]="operations/quality/metrics/docs"
        ["operations-excellence"]="operations/quality/metrics/docs"
        ["financial"]="business/financial/reports/docs"
        ["financial-analysis"]="business/financial/reports/docs"
        ["investor"]="business/investor/relations/docs"
        ["legal"]="business/legal/contracts/docs"
        ["marketing"]="business/marketing/campaigns/docs"
        ["market-intelligence"]="business/marketing/campaigns/docs"
        ["hr"]="people/hr/policies/docs"
        ["employees"]="people/employees/leadership/docs"
        ["organization"]="people/employees/teams/docs"
        ["partners"]="external/partners/integrations/docs"
        ["partnerships"]="external/partners/integrations/docs"
        ["customers"]="external/customers/implementations/docs"
        ["customer-implementations"]="external/customers/implementations/docs"
        ["competitors"]="external/competitors/analysis/docs"
        ["community"]="external/community/outreach/docs"
        ["projects"]="projects/atlas/documentation/docs"
        ["compliance"]="governance/compliance/regulations/docs"
        ["policies"]="governance/policies/standards/docs"
        ["governance"]="governance/policies/standards/docs"
        ["meetings"]="governance/meetings/board/docs"
        ["acquisitions"]="business/legal/contracts/docs"
        ["incidents"]="operations/quality/metrics/docs"
        ["international"]="external/partners/integrations/docs"
        ["patents"]="business/legal/contracts/docs"
        ["products"]="projects/atlas/documentation/docs"
        ["security"]="governance/compliance/regulations/docs"
        ["sustainability"]="operations/facilities/locations/docs"
        ["technology"]="engineering/tech/docs"
        ["training"]="people/hr/policies/docs"
        ["vendor-management"]="external/partners/integrations/docs"
    )

    # Copy files to deep structure
    for dir in "$SOURCE_DIR"/*/; do
        if [ -d "$dir" ]; then
            dir_name=$(basename "$dir")
            target_subdir="${DIR_MAP[$dir_name]:-engineering/tech/docs}"

            # Copy all .md files
            find "$dir" -name "*.md" -exec cp {} "$BASE/$target_subdir/" \; 2>/dev/null || true
        fi
    done

    local file_count=$(find "$TARGET_DIR" -name "*.md" | wc -l)
    local max_depth=$(find "$TARGET_DIR" -type f -name "*.md" | sed 's|[^/]||g' | sort -r | head -1 | wc -c)
    echo "  Created very-deep-v6 with $file_count files, max depth: $((max_depth-1)) levels"
}

# ============================================
# Main
# ============================================

echo "Source: $SOURCE_DIR"
echo "Source file count: $(find "$SOURCE_DIR" -name "*.md" | wc -l)"

build_shallow
build_very_deep

echo ""
echo "================================================"
echo "  Build Complete"
echo "================================================"
echo ""
echo "New structures:"
ls -la "$PROJECT_ROOT/soong-daystrom/" | grep v6

echo ""
echo "To run tests:"
echo "  ./harness/run-v6-extended-matrix.sh"
