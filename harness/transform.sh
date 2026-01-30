#!/bin/bash
#
# Transform source content into different structure variants
# Creates: monolith, flat, shallow, deep, very-deep
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$PROJECT_ROOT/soong-daystrom/_source"
STRUCTURES_DIR="$PROJECT_ROOT/soong-daystrom"

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

# Ensure source exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Count source files
SOURCE_COUNT=$(find "$SOURCE_DIR" -name "*.md" | wc -l)
log "Found $SOURCE_COUNT source files"

#######################################
# MONOLITH: Single file with all content
#######################################
create_monolith() {
    log "Creating monolith structure..."
    local TARGET="$STRUCTURES_DIR/monolith"
    mkdir -p "$TARGET"

    # Combine all files into one
    local OUTPUT="$TARGET/company-documentation.md"
    echo "# Soong-Daystrom Industries Complete Documentation" > "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "This document contains all company documentation in a single file." >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    # Add each file with section headers
    find "$SOURCE_DIR" -name "*.md" -type f | sort | while read -r file; do
        local relpath="${file#$SOURCE_DIR/}"
        local category=$(dirname "$relpath")
        local filename=$(basename "$relpath" .md)

        echo "# $category / $filename" >> "$OUTPUT"
        echo "" >> "$OUTPUT"
        cat "$file" >> "$OUTPUT"
        echo "" >> "$OUTPUT"
        echo "---" >> "$OUTPUT"
        echo "" >> "$OUTPUT"
    done

    # Create CLAUDE.md
    cat > "$TARGET/CLAUDE.md" << 'EOF'
# Soong-Daystrom Industries Context

You are answering questions about Soong-Daystrom Industries, a fictional robotics and AI company.

## Available Documentation

All company documentation is in a single file:
- @company-documentation.md - Complete company documentation

Use this file to answer questions about the company.
EOF

    log "Monolith created: $(wc -w < "$OUTPUT") words"
}

#######################################
# FLAT: All files in root, no hierarchy
#######################################
create_flat() {
    log "Creating flat structure..."
    local TARGET="$STRUCTURES_DIR/flat"
    mkdir -p "$TARGET"

    # Copy all files to flat structure with prefixed names
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        local relpath="${file#$SOURCE_DIR/}"
        local category=$(dirname "$relpath")
        local filename=$(basename "$relpath" .md)
        local newname="${category}-${filename}.md"
        # Replace / with - for nested paths
        newname=$(echo "$newname" | tr '/' '-')
        cp "$file" "$TARGET/$newname"
    done

    # Create CLAUDE.md with file list
    cat > "$TARGET/CLAUDE.md" << 'EOF'
# Soong-Daystrom Industries Context

You are answering questions about Soong-Daystrom Industries, a fictional robotics and AI company.

## Available Documentation

EOF

    # Add file references
    for file in "$TARGET"/*.md; do
        [[ $(basename "$file") == "CLAUDE.md" ]] && continue
        local name=$(basename "$file" .md)
        echo "- @$name.md" >> "$TARGET/CLAUDE.md"
    done

    log "Flat created: $(ls "$TARGET"/*.md | wc -l) files"
}

#######################################
# SHALLOW: 2-level hierarchy (category/file)
#######################################
create_shallow() {
    log "Creating shallow structure..."
    local TARGET="$STRUCTURES_DIR/shallow"
    mkdir -p "$TARGET"

    # Copy preserving one level of hierarchy
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        local relpath="${file#$SOURCE_DIR/}"
        local category=$(dirname "$relpath" | cut -d'/' -f1)
        local filename=$(basename "$relpath")

        mkdir -p "$TARGET/$category"
        cp "$file" "$TARGET/$category/$filename"
    done

    # Create CLAUDE.md
    cat > "$TARGET/CLAUDE.md" << 'EOF'
# Soong-Daystrom Industries Context

You are answering questions about Soong-Daystrom Industries, a fictional robotics and AI company.

## Documentation Structure

EOF

    # Add category sections
    for category in employees financial history meetings organization policies products projects; do
        if [[ -d "$TARGET/$category" ]]; then
            echo "### ${category^}" >> "$TARGET/CLAUDE.md"
            for file in "$TARGET/$category"/*.md; do
                [[ -f "$file" ]] || continue
                local name=$(basename "$file" .md)
                echo "- @$category/$name.md" >> "$TARGET/CLAUDE.md"
            done
            echo "" >> "$TARGET/CLAUDE.md"
        fi
    done

    log "Shallow created: $(find "$TARGET" -name "*.md" ! -name "CLAUDE.md" | wc -l) files in $(find "$TARGET" -type d | wc -l) directories"
}

#######################################
# DEEP: 3-4 level hierarchy
#######################################
create_deep() {
    log "Creating deep structure..."
    local TARGET="$STRUCTURES_DIR/deep"
    mkdir -p "$TARGET"

    # Create deeper structure by adding domain subdirectories
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        local relpath="${file#$SOURCE_DIR/}"
        local category=$(dirname "$relpath" | cut -d'/' -f1)
        local filename=$(basename "$relpath" .md)

        # Create deeper paths based on category and file type
        case "$category" in
            organization)
                if [[ "$filename" == "executives" ]]; then
                    mkdir -p "$TARGET/company/structure/leadership"
                    cp "$file" "$TARGET/company/structure/leadership/$filename.md"
                elif [[ "$filename" == "departments" ]]; then
                    mkdir -p "$TARGET/company/structure/departments"
                    cp "$file" "$TARGET/company/structure/departments/$filename.md"
                else
                    mkdir -p "$TARGET/company/structure/other"
                    cp "$file" "$TARGET/company/structure/other/$filename.md"
                fi
                ;;
            projects)
                mkdir -p "$TARGET/company/initiatives/projects"
                cp "$file" "$TARGET/company/initiatives/projects/$filename.md"
                ;;
            products)
                mkdir -p "$TARGET/company/offerings/products"
                cp "$file" "$TARGET/company/offerings/products/$filename.md"
                ;;
            financial)
                mkdir -p "$TARGET/company/finance/reports"
                cp "$file" "$TARGET/company/finance/reports/$filename.md"
                ;;
            employees)
                mkdir -p "$TARGET/company/people/directory"
                cp "$file" "$TARGET/company/people/directory/$filename.md"
                ;;
            history)
                mkdir -p "$TARGET/company/background/history"
                cp "$file" "$TARGET/company/background/history/$filename.md"
                ;;
            policies)
                mkdir -p "$TARGET/company/governance/policies"
                cp "$file" "$TARGET/company/governance/policies/$filename.md"
                ;;
            meetings)
                mkdir -p "$TARGET/company/records/meetings"
                cp "$file" "$TARGET/company/records/meetings/$filename.md"
                ;;
            *)
                mkdir -p "$TARGET/company/other"
                cp "$file" "$TARGET/company/other/$filename.md"
                ;;
        esac
    done

    # Create CLAUDE.md with full hierarchy
    cat > "$TARGET/CLAUDE.md" << 'EOF'
# Soong-Daystrom Industries Context

You are answering questions about Soong-Daystrom Industries, a fictional robotics and AI company.

## Documentation Structure

### Company
- @company/structure/leadership/ - Executive team
- @company/structure/departments/ - Department information
- @company/initiatives/projects/ - Active projects
- @company/offerings/products/ - Product lines
- @company/finance/reports/ - Financial reports
- @company/people/directory/ - Employee directory
- @company/background/history/ - Company history
- @company/governance/policies/ - Company policies
- @company/records/meetings/ - Meeting minutes

Use the appropriate files to answer questions about the company.
EOF

    log "Deep created: $(find "$TARGET" -name "*.md" ! -name "CLAUDE.md" | wc -l) files in $(find "$TARGET" -type d | wc -l) directories"
}

#######################################
# VERY-DEEP: 5+ level hierarchy
#######################################
create_very_deep() {
    log "Creating very-deep structure..."
    local TARGET="$STRUCTURES_DIR/very-deep"
    mkdir -p "$TARGET"

    # Create maximum depth structure
    find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
        local relpath="${file#$SOURCE_DIR/}"
        local category=$(dirname "$relpath" | cut -d'/' -f1)
        local filename=$(basename "$relpath" .md)

        case "$category" in
            organization)
                if [[ "$filename" == "executives" ]]; then
                    mkdir -p "$TARGET/soong-daystrom/company/structure/leadership/executive-team"
                    cp "$file" "$TARGET/soong-daystrom/company/structure/leadership/executive-team/$filename.md"
                elif [[ "$filename" == "departments" ]]; then
                    mkdir -p "$TARGET/soong-daystrom/company/structure/organization/departments"
                    cp "$file" "$TARGET/soong-daystrom/company/structure/organization/departments/$filename.md"
                else
                    mkdir -p "$TARGET/soong-daystrom/company/structure/other/misc"
                    cp "$file" "$TARGET/soong-daystrom/company/structure/other/misc/$filename.md"
                fi
                ;;
            projects)
                mkdir -p "$TARGET/soong-daystrom/company/initiatives/research/active-projects"
                cp "$file" "$TARGET/soong-daystrom/company/initiatives/research/active-projects/$filename.md"
                ;;
            products)
                mkdir -p "$TARGET/soong-daystrom/company/business/offerings/product-lines"
                cp "$file" "$TARGET/soong-daystrom/company/business/offerings/product-lines/$filename.md"
                ;;
            financial)
                mkdir -p "$TARGET/soong-daystrom/company/finance/accounting/reports"
                cp "$file" "$TARGET/soong-daystrom/company/finance/accounting/reports/$filename.md"
                ;;
            employees)
                mkdir -p "$TARGET/soong-daystrom/company/people/hr/employee-directory"
                cp "$file" "$TARGET/soong-daystrom/company/people/hr/employee-directory/$filename.md"
                ;;
            history)
                mkdir -p "$TARGET/soong-daystrom/company/background/corporate-history/timeline"
                cp "$file" "$TARGET/soong-daystrom/company/background/corporate-history/timeline/$filename.md"
                ;;
            policies)
                mkdir -p "$TARGET/soong-daystrom/company/governance/compliance/policies"
                cp "$file" "$TARGET/soong-daystrom/company/governance/compliance/policies/$filename.md"
                ;;
            meetings)
                mkdir -p "$TARGET/soong-daystrom/company/records/documentation/meeting-minutes"
                cp "$file" "$TARGET/soong-daystrom/company/records/documentation/meeting-minutes/$filename.md"
                ;;
            *)
                mkdir -p "$TARGET/soong-daystrom/company/other/uncategorized"
                cp "$file" "$TARGET/soong-daystrom/company/other/uncategorized/$filename.md"
                ;;
        esac
    done

    # Create CLAUDE.md
    cat > "$TARGET/CLAUDE.md" << 'EOF'
# Soong-Daystrom Industries Context

You are answering questions about Soong-Daystrom Industries, a fictional robotics and AI company.

## Documentation Structure

The documentation is organized in a deep hierarchy under `soong-daystrom/company/`:

### Structure
- @soong-daystrom/company/structure/leadership/executive-team/ - Executives
- @soong-daystrom/company/structure/organization/departments/ - Departments

### Initiatives
- @soong-daystrom/company/initiatives/research/active-projects/ - Projects

### Business
- @soong-daystrom/company/business/offerings/product-lines/ - Products

### Finance
- @soong-daystrom/company/finance/accounting/reports/ - Financial reports

### People
- @soong-daystrom/company/people/hr/employee-directory/ - Employees

### Background
- @soong-daystrom/company/background/corporate-history/timeline/ - History

### Governance
- @soong-daystrom/company/governance/compliance/policies/ - Policies

### Records
- @soong-daystrom/company/records/documentation/meeting-minutes/ - Meetings

Navigate to the appropriate directory to find relevant information.
EOF

    log "Very-deep created: $(find "$TARGET" -name "*.md" ! -name "CLAUDE.md" | wc -l) files in $(find "$TARGET" -type d | wc -l) directories"
}

#######################################
# Main
#######################################

log "Starting structure transformation..."
log "Source: $SOURCE_DIR"
log "Target: $STRUCTURES_DIR"

create_monolith
create_flat
create_shallow
create_deep
create_very_deep

log ""
log "Transformation complete!"
log ""
log "Structure summary:"
for struct in monolith flat shallow deep very-deep; do
    local dir="$STRUCTURES_DIR/$struct"
    local files=$(find "$dir" -name "*.md" ! -name "CLAUDE.md" 2>/dev/null | wc -l)
    local dirs=$(find "$dir" -type d 2>/dev/null | wc -l)
    echo "  $struct: $files files, $dirs directories"
done
