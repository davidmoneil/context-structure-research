#!/usr/bin/env python3
"""
Generate LLM-dependent strategy artifacts without API calls.

Reads the keyword indexes and source files to produce:
- I2: relationships.md (topic-based connections from keyword overlap)
- I3: capabilities.md (semantic groupings by directory + topic)
- I4: summaries.md (one-sentence summary per file)
- C2: CLAUDE.md combining R4 refs + I2 relationships
- R2.2: CLAUDE.md with @refs + 1-sentence summaries
- R2.4: CLAUDE.md with @refs + 2-sentence summaries
"""

import json
import os
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STRATEGIES_DIR = PROJECT_ROOT / "strategies"
SOONG_SOURCE = PROJECT_ROOT / "soong-daystrom" / "_source-v5"
OBSIDIAN_SOURCE = PROJECT_ROOT / "test-datasets" / "obsidian"

DATASETS = {
    "soong-v5": SOONG_SOURCE,
    "obsidian": OBSIDIAN_SOURCE,
}


def get_md_files(source_dir: Path) -> list[Path]:
    """Get all .md files in a directory, sorted."""
    files = sorted(source_dir.rglob("*.md"))
    return [f for f in files if f.name != "questions.json"]


def relative_data_path(file_path: Path, source_dir: Path) -> str:
    rel = file_path.relative_to(source_dir)
    return f"data/{rel}"


def parse_keyword_index(index_path: Path) -> dict[str, list[str]]:
    """Parse the I1 keyword index into {file_path: [keywords]}."""
    result = {}
    text = index_path.read_text()
    for line in text.split("\n"):
        match = re.match(r'\| `([^`]+)` \| (.+) \|', line)
        if match:
            file_path = match.group(1)
            keywords = [k.strip() for k in match.group(2).split(",")]
            result[file_path] = keywords
    return result


def humanize_filename(filename: str) -> str:
    """Convert filename to readable form: kebab-case → Title Words."""
    name = Path(filename).stem
    # Handle various separators
    name = name.replace("-", " ").replace("_", " ")
    # Remove date prefixes like "2026.02.18_" or "2026-01-21-"
    name = re.sub(r'^\d{4}[\.\-]\d{2}[\.\-]\d{2}[\s_\-]*', '', name)
    return name.strip()


def get_file_summary(file_path: str, keywords: list[str], source_dir: Path, dataset: str) -> str:
    """Generate a one-sentence summary from filename, keywords, and directory context."""
    parts = Path(file_path.replace("data/", "")).parts
    directory = parts[0] if len(parts) > 1 else ""
    subdirectory = parts[1] if len(parts) > 2 else ""
    filename = humanize_filename(parts[-1])

    # Read first 200 words for additional context
    full_path = source_dir / Path(file_path.replace("data/", ""))
    first_words = ""
    if full_path.exists():
        text = full_path.read_text(errors='replace')
        # Extract first heading if available
        heading_match = re.search(r'^#+ (.+)$', text, re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else ""
        first_words = " ".join(text.split()[:150])
    else:
        heading = ""

    # Build contextual summary based on dataset and directory
    if dataset == "soong-v5":
        return _summarize_soong(file_path, directory, subdirectory, filename, keywords, heading, first_words)
    else:
        return _summarize_obsidian(file_path, directory, subdirectory, filename, keywords, heading, first_words)


def _summarize_soong(file_path: str, directory: str, subdirectory: str, filename: str, keywords: list[str], heading: str, first_words: str) -> str:
    """Generate summary for Soong-Daystrom Industries files."""
    kw = ", ".join(keywords[:4])
    dir_label = directory.replace("-", " ").title()

    # Use heading when available and informative
    if heading and len(heading) > 10:
        title = heading
    else:
        title = filename

    # Directory-specific summaries
    summaries = {
        "financial": f"Financial data covering {title.lower()}, with metrics on {kw}.",
        "products": f"Product documentation for {title}, covering {kw}.",
        "technical": f"Technical specifications and documentation for {title}, including {kw}.",
        "employees": f"Employee records and team information for {title}, covering {kw}.",
        "projects": f"Project documentation for {title}, with details on {kw}.",
        "meetings": f"Meeting records for {title}, discussing {kw}.",
        "history": f"Historical documentation about {title}, covering {kw}.",
        "organization": f"Organizational structure information about {title}, including {kw}.",
        "policies": f"Policy documentation for {title}, addressing {kw}.",
        "legal": f"Legal and compliance information about {title}, covering {kw}.",
        "operations": f"Operations documentation for {title}, including {kw}.",
        "facilities": f"Facility details for {title}, covering {kw}.",
        "regions": f"Regional operations information for {title}, with data on {kw}.",
        "customers": f"Customer information about {title}, including {kw}.",
        "competitors": f"Competitive analysis covering {title}, with data on {kw}.",
        "hr": f"Human resources documentation for {title}, addressing {kw}.",
        "research": f"Research documentation about {title}, covering {kw}.",
        "sales": f"Sales and channel information for {title}, with data on {kw}.",
        "security": f"Security documentation for {title}, covering {kw}.",
        "support": f"Customer support and service information for {title}, including {kw}.",
        "training": f"Training and development information for {title}, covering {kw}.",
        "marketing": f"Marketing documentation for {title}, with data on {kw}.",
        "investor": f"Investor relations information about {title}, covering {kw}.",
        "partners": f"Partnership and alliance details for {title}, including {kw}.",
        "governance": f"Corporate governance documentation for {title}, addressing {kw}.",
        "community": f"Community program information about {title}, covering {kw}.",
    }

    return summaries.get(directory, f"Documentation about {title}, covering {kw}.")


def _summarize_obsidian(file_path: str, directory: str, subdirectory: str, filename: str, keywords: list[str], heading: str, first_words: str) -> str:
    """Generate summary for Obsidian vault files."""
    kw = ", ".join(keywords[:4])

    if heading and len(heading) > 10:
        title = heading
    else:
        title = filename

    # Determine content type from path
    path_lower = file_path.lower()

    if "ciso-expert/posts/" in path_lower:
        return f"Published blog post: {title}, discussing {kw}."
    elif "ciso-expert/drafts/" in path_lower:
        return f"Draft article: {title}, covering {kw}."
    elif "ciso-expert/pages/" in path_lower:
        return f"Website page: {title}, about {kw}."
    elif "ciso-expert/archive/" in path_lower:
        return f"Archived article: {title}, covering {kw}."
    elif "claude-knowledge/discoveries/" in path_lower:
        return f"Discovery notes: {title}, documenting findings about {kw}."
    elif "claude-knowledge/patterns/" in path_lower:
        return f"Design pattern: {title}, describing approach for {kw}."
    elif "claude-knowledge/research/" in path_lower:
        return f"Research notes: {title}, investigating {kw}."
    elif "claude-knowledge/session-notes/" in path_lower:
        return f"Session notes: {title}, covering work on {kw}."
    elif "architecture/" in path_lower:
        return f"Architecture documentation: {title}, describing {kw}."
    elif "infrastructure/" in path_lower:
        return f"Infrastructure notes: {title}, covering {kw}."
    elif "projects/docker/" in path_lower:
        return f"Docker configuration: {title}, with setup for {kw}."
    elif "projects/headless-claude/" in path_lower:
        return f"Headless Claude project: {title}, describing {kw}."
    elif "projects/recon tool/" in path_lower or "projects/osint/" in path_lower:
        return f"Security/OSINT project: {title}, covering {kw}."
    elif "projects/loom/" in path_lower:
        return f"Project Loom: {title}, exploring {kw}."
    elif "projects/n8n/" in path_lower:
        return f"N8N workflow notes: {title}, covering {kw}."
    elif "projects/" in path_lower:
        return f"Project notes: {title}, covering {kw}."
    elif "research/" in path_lower:
        return f"Research document: {title}, investigating {kw}."
    else:
        return f"Knowledge base document: {title}, covering {kw}."


def get_file_summary_extended(file_path: str, keywords: list[str], source_dir: Path, dataset: str) -> str:
    """Generate a two-sentence summary for R2.4."""
    one_sentence = get_file_summary(file_path, keywords, source_dir, dataset)
    kw_extra = ", ".join(keywords[4:]) if len(keywords) > 4 else ", ".join(keywords[:3])
    return f"{one_sentence} Additional topics include {kw_extra}."


# ─── I2: Relationships ──────────────────────────────────────────────

def build_I2(dataset: str, source_dir: Path, keyword_index: dict):
    """Build relationships.md from keyword overlap."""
    strategy_dir = STRATEGIES_DIR / dataset / "I2"

    # Index: keyword → list of file paths
    keyword_to_files = defaultdict(list)
    for file_path, keywords in keyword_index.items():
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower and len(kw_lower) > 2:
                keyword_to_files[kw_lower].append(file_path)

    # Filter: only keywords connecting 2+ files, up to 15 files (not too generic)
    connections = {}
    for kw, files in keyword_to_files.items():
        if 2 <= len(files) <= 15:
            connections[kw] = sorted(files)

    # Also build higher-level topic connections by directory grouping
    # Group files that share 3+ keywords (stronger connections)
    file_pairs = defaultdict(int)
    files_list = list(keyword_index.keys())
    for i in range(len(files_list)):
        kw_i = set(keyword_index[files_list[i]])
        for j in range(i + 1, len(files_list)):
            kw_j = set(keyword_index[files_list[j]])
            shared = kw_i & kw_j
            if len(shared) >= 3:
                file_pairs[(files_list[i], files_list[j])] = len(shared)

    # Build the relationship document
    lines = ["# File Relationship Graph\n"]
    lines.append("This graph shows connections between files based on shared topics.\n")
    lines.append(f"**{len(connections)} shared topics found across {len(keyword_index)} files.**\n")

    for topic in sorted(connections.keys()):
        refs = connections[topic]
        lines.append(f"## {topic.title()}")
        for ref in refs:
            lines.append(f"- `{ref}`")
        lines.append("")

    (strategy_dir / "relationships.md").write_text("\n".join(lines) + "\n")

    # CLAUDE.md
    claude_lines = [
        "# Knowledge Base with Relationship Graph\n",
        "Use the relationship graph to find connected files, then read those files to answer questions.\n",
        "@relationships.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")

    size = (strategy_dir / "relationships.md").stat().st_size
    print(f"  BUILT I2/{dataset} — {len(connections)} topics, {size:,} bytes")


# ─── I3: Semantic Groupings ─────────────────────────────────────────

def build_I3_soong(dataset: str, keyword_index: dict):
    """Build capabilities.md for soong-v5 using directory structure + topics."""
    strategy_dir = STRATEGIES_DIR / dataset / "I3"

    # Group by directory
    dir_groups = defaultdict(list)
    for file_path in keyword_index:
        parts = Path(file_path.replace("data/", "")).parts
        if len(parts) > 1:
            dir_groups[parts[0]].append(file_path)
        else:
            dir_groups["root"].append(file_path)

    # Define meaningful semantic groups that cut across directories
    groups = {
        "Financial & Business Performance": {
            "desc": "Revenue, budgets, quarterly reports, investor materials, and segment analysis.",
            "dirs": ["financial", "investor"],
        },
        "Products & Technology": {
            "desc": "Product lines (PCS, NIM, IAP, SCE), technical specifications, and architecture.",
            "dirs": ["products", "technical"],
        },
        "Research & Innovation": {
            "desc": "Research initiatives, consciousness research, and publications.",
            "dirs": ["research"],
            "keywords": ["consciousness", "research", "positronic"],
        },
        "Projects & Programs": {
            "desc": "Active projects including Prometheus, Atlas, Hermes, and completed projects.",
            "dirs": ["projects"],
        },
        "People & Organization": {
            "desc": "Employee directories, leadership, departments, and team structure.",
            "dirs": ["employees", "organization"],
        },
        "Human Resources & Training": {
            "desc": "Benefits, compensation, performance management, training, and certifications.",
            "dirs": ["hr", "training"],
        },
        "Operations & Facilities": {
            "desc": "Manufacturing operations, supply chain, facilities, and quality management.",
            "dirs": ["operations", "facilities"],
        },
        "Governance, Legal & Compliance": {
            "desc": "Board governance, legal framework, regulatory compliance, and policies.",
            "dirs": ["governance", "legal", "policies"],
        },
        "Sales, Marketing & Customers": {
            "desc": "Customer accounts, market research, pricing, brand guidelines, and sales channels.",
            "dirs": ["sales", "marketing", "customers", "competitors"],
        },
        "Global Operations & Regions": {
            "desc": "Regional operations across Americas, EMEA, Asia-Pacific, and global supply chain.",
            "dirs": ["regions"],
        },
        "Meetings & Communications": {
            "desc": "Board meetings, executive committee meetings, all-hands transcripts, and product reviews.",
            "dirs": ["meetings"],
        },
        "Security & Risk": {
            "desc": "Cybersecurity policies, security protocols, crisis management, and data governance.",
            "dirs": ["security"],
            "keywords": ["security", "crisis", "privacy"],
        },
        "Partnerships & Community": {
            "desc": "Strategic partnerships, alliances, and community engagement programs.",
            "dirs": ["partners", "community"],
        },
        "Customer Support": {
            "desc": "Customer service operations, support processes, and knowledge bases.",
            "dirs": ["support"],
        },
        "Company History": {
            "desc": "Founding story, major milestones, acquisitions, and historical events.",
            "dirs": ["history"],
        },
    }

    lines = ["# Knowledge Base — Semantic Groupings\n"]
    lines.append(f"Files organized into {len(groups)} topic groups.\n")

    for group_name, info in groups.items():
        matching_files = []
        for dir_name in info.get("dirs", []):
            matching_files.extend(dir_groups.get(dir_name, []))

        # Also find files matching keywords if specified
        if "keywords" in info:
            for file_path, kws in keyword_index.items():
                if file_path not in matching_files:
                    if any(k in kws for k in info["keywords"]):
                        matching_files.append(file_path)

        if matching_files:
            lines.append(f"## {group_name}")
            lines.append(f"*{info['desc']}*\n")
            for f in sorted(set(matching_files)):
                lines.append(f"- `{f}`")
            lines.append("")

    (strategy_dir / "capabilities.md").write_text("\n".join(lines) + "\n")

    claude_lines = [
        "# Knowledge Base with Semantic Groupings\n",
        "Files are organized by topic. Use the groupings to find relevant files, then read them.\n",
        "@capabilities.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")

    size = (strategy_dir / "capabilities.md").stat().st_size
    print(f"  BUILT I3/{dataset} — {len(groups)} groups, {size:,} bytes")


def build_I3_obsidian(dataset: str, keyword_index: dict):
    """Build capabilities.md for obsidian using directory structure + topics."""
    strategy_dir = STRATEGIES_DIR / dataset / "I3"

    groups = {
        "Claude Code Architecture & Patterns": {
            "desc": "AIProjects architecture, question flow, design patterns, and configuration.",
            "match": ["architecture/", "infrastructure/", "design pattern"],
        },
        "Claude Code Research": {
            "desc": "Research on Claude Code features, customization, plugins, memory, and teams.",
            "match": ["claude-knowledge/research/"],
        },
        "Claude Code Discoveries & Session Notes": {
            "desc": "Operational discoveries, health checks, troubleshooting, and session documentation.",
            "match": ["claude-knowledge/discoveries/", "claude-knowledge/session-notes/"],
        },
        "Claude Code Patterns": {
            "desc": "Documented patterns for MCP loading, agent selection, memory, automation, and more.",
            "match": ["claude-knowledge/patterns/"],
        },
        "CISO Expert — Published Content": {
            "desc": "Published blog posts and articles on cybersecurity, incident response, and Claude Code.",
            "match": ["ciso-expert/posts/"],
        },
        "CISO Expert — Drafts": {
            "desc": "Draft articles on cybersecurity, SOAR, SIEM, vulnerability management, and AI context.",
            "match": ["ciso-expert/drafts/"],
        },
        "CISO Expert — Website Pages": {
            "desc": "Service pages for penetration testing, virtual CISO, tabletop exercises, and security tools.",
            "match": ["ciso-expert/pages/"],
        },
        "CISO Expert — Archive": {
            "desc": "Archived articles on Claude Code context research and accuracy testing.",
            "match": ["ciso-expert/archive/"],
        },
        "Docker & Infrastructure Projects": {
            "desc": "Docker configurations for various services (N8N, MISP, AudiobookShelf, OpenWebUI, etc.).",
            "match": ["projects/docker/", "home enviornment"],
        },
        "Security & OSINT Projects": {
            "desc": "Kali Scanner pipeline, SpiderFoot, reconnaissance tools, and security scanning.",
            "match": ["projects/osint/", "projects/recon tool/", "kali-scanner"],
        },
        "Headless Claude & Automation": {
            "desc": "Headless Claude design, implementation guides, and automation projects.",
            "match": ["projects/headless-claude/"],
        },
        "AI Research & Context Orchestration": {
            "desc": "Research on context orchestration, LLM evaluation, token efficiency, and best practices.",
            "match": ["research/"],
        },
        "Project Management & Workflow": {
            "desc": "Active projects, N8N workflows, Beads task management, and project planning.",
            "match": ["projects/n8n/", "projects/_", "projects/active", "beads"],
        },
        "Miscellaneous Projects": {
            "desc": "Audio/voice projects, Obsidian sync, Teleport deployment, and other tools.",
            "match": ["projects/voice", "projects/audio", "projects/obsidian", "projects/teleport",
                      "projects/sumo", "projects/outlook", "projects/doctor who",
                      "projects/loom/", "projects/fabric", "projects/homelab",
                      "projects/mcp_connector"],
        },
        "Voice of David & Personal": {
            "desc": "Communication preferences, personal voice documentation, and interaction patterns.",
            "match": ["voice-of-david"],
        },
    }

    lines = ["# Knowledge Base — Semantic Groupings\n"]
    lines.append(f"Files organized into {len(groups)} topic groups.\n")

    used_files = set()
    for group_name, info in groups.items():
        matching_files = []
        for file_path in keyword_index:
            path_lower = file_path.lower()
            if any(m.lower() in path_lower for m in info["match"]):
                matching_files.append(file_path)
                used_files.add(file_path)

        if matching_files:
            lines.append(f"## {group_name}")
            lines.append(f"*{info['desc']}*\n")
            for f in sorted(set(matching_files)):
                lines.append(f"- `{f}`")
            lines.append("")

    # Catch any ungrouped files
    ungrouped = [f for f in keyword_index if f not in used_files]
    if ungrouped:
        lines.append("## Other")
        lines.append("*Files not fitting into the above categories.*\n")
        for f in sorted(ungrouped):
            lines.append(f"- `{f}`")
        lines.append("")

    (strategy_dir / "capabilities.md").write_text("\n".join(lines) + "\n")

    claude_lines = [
        "# Knowledge Base with Semantic Groupings\n",
        "Files are organized by topic. Use the groupings to find relevant files, then read them.\n",
        "@capabilities.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")

    size = (strategy_dir / "capabilities.md").stat().st_size
    print(f"  BUILT I3/{dataset} — groups, {size:,} bytes")


# ─── I4: Summary Index ──────────────────────────────────────────────

def build_I4(dataset: str, source_dir: Path, keyword_index: dict):
    """Build summaries.md with one-sentence summary per file."""
    strategy_dir = STRATEGIES_DIR / dataset / "I4"

    lines = ["# Summary Index\n"]
    lines.append("Each file in the knowledge base with a brief summary.\n")
    lines.append("| File | Summary |")
    lines.append("|------|---------|")

    for file_path in sorted(keyword_index.keys()):
        keywords = keyword_index[file_path]
        summary = get_file_summary(file_path, keywords, source_dir, dataset)
        summary = summary.replace("|", "\\|")
        lines.append(f"| `{file_path}` | {summary} |")

    (strategy_dir / "summaries.md").write_text("\n".join(lines) + "\n")

    claude_lines = [
        "# Knowledge Base with Summary Index\n",
        "Use the summary index to identify relevant files, then read them for details.\n",
        "@summaries.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")

    size = (strategy_dir / "summaries.md").stat().st_size
    print(f"  BUILT I4/{dataset} — {len(keyword_index)} summaries, {size:,} bytes")


# ─── C2: R4 + I2 Combined ───────────────────────────────────────────

def build_C2(dataset: str, source_dir: Path, keyword_index: dict):
    """Build C2: R4 (selective refs) + I2 (relationships) combined."""
    strategy_dir = STRATEGIES_DIR / dataset / "C2"

    # Copy relationships.md from I2
    i2_rels = STRATEGIES_DIR / dataset / "I2" / "relationships.md"
    if i2_rels.exists():
        shutil.copy2(i2_rels, strategy_dir / "relationships.md")
    else:
        print(f"  ERROR: I2 relationships not found for {dataset}")
        return

    # Get R4 key files
    r4_claude = STRATEGIES_DIR / dataset / "R4" / "CLAUDE.md"
    r4_refs = []
    if r4_claude.exists():
        for line in r4_claude.read_text().split("\n"):
            if line.startswith("@data/"):
                r4_refs.append(line)

    lines = ["# Key Files with Relationship Graph\n"]
    lines.append(f"The {len(r4_refs)} most important files are listed below. ")
    lines.append("Use the relationship graph to discover connected files.\n")
    lines.append("@relationships.md\n")
    for ref in r4_refs:
        lines.append(ref)

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")

    size = (strategy_dir / "relationships.md").stat().st_size
    print(f"  BUILT C2/{dataset} — {len(r4_refs)} key refs + relationships ({size:,} bytes)")


# ─── R2.2: @refs + 1-sentence summary ───────────────────────────────

def build_R2_2(dataset: str, source_dir: Path, keyword_index: dict):
    """Build R2.2: whole-file @refs with 1-sentence summaries."""
    strategy_dir = STRATEGIES_DIR / dataset / "R2.2"

    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. One-sentence summaries describe each file.\n")

    for file_path in sorted(keyword_index.keys()):
        keywords = keyword_index[file_path]
        ref = file_path  # already has data/ prefix
        summary = get_file_summary(file_path, keywords, source_dir, dataset)
        lines.append(f"@{ref} — {summary}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")

    size = (strategy_dir / "CLAUDE.md").stat().st_size
    print(f"  BUILT R2.2/{dataset} — {len(keyword_index)} refs + summaries, {size:,} bytes")


# ─── R2.4: @refs + 2-sentence summary ───────────────────────────────

def build_R2_4(dataset: str, source_dir: Path, keyword_index: dict):
    """Build R2.4: whole-file @refs with 2-sentence summaries."""
    strategy_dir = STRATEGIES_DIR / dataset / "R2.4"

    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. Two-sentence summaries describe each file.\n")

    for file_path in sorted(keyword_index.keys()):
        keywords = keyword_index[file_path]
        ref = file_path
        summary = get_file_summary_extended(file_path, keywords, source_dir, dataset)
        lines.append(f"@{ref} — {summary}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")

    size = (strategy_dir / "CLAUDE.md").stat().st_size
    print(f"  BUILT R2.4/{dataset} — {len(keyword_index)} refs + summaries, {size:,} bytes")


# ─── Main ────────────────────────────────────────────────────────────

def main():
    print("\n=== Generating LLM-dependent strategy artifacts ===\n")

    for dataset, source_dir in DATASETS.items():
        print(f"\n--- Dataset: {dataset} ---")

        # Read keyword index from I1
        index_path = STRATEGIES_DIR / dataset / "I1" / "index.md"
        if not index_path.exists():
            print(f"  ERROR: No keyword index at {index_path}")
            continue

        keyword_index = parse_keyword_index(index_path)
        print(f"  Loaded {len(keyword_index)} files from keyword index")

        # Build strategies in dependency order
        build_I2(dataset, source_dir, keyword_index)

        if dataset == "soong-v5":
            build_I3_soong(dataset, keyword_index)
        else:
            build_I3_obsidian(dataset, keyword_index)

        build_I4(dataset, source_dir, keyword_index)
        build_C2(dataset, source_dir, keyword_index)
        build_R2_2(dataset, source_dir, keyword_index)
        build_R2_4(dataset, source_dir, keyword_index)

    print("\n=== Done! All LLM-dependent strategies generated. ===\n")


if __name__ == "__main__":
    main()
