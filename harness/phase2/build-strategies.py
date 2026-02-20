#!/usr/bin/env python3
"""
Phase 2: Build strategy folders with symlinks, CLAUDE.md files, and index artifacts.

Creates the folder-per-strategy structure:
  strategies/<dataset>/<strategy>/
    ├── data -> symlink to corpus
    ├── CLAUDE.md (strategy-specific)
    └── index.md / relationships.md / etc. (if applicable)

Usage:
    python3 build-strategies.py                    # Build all non-LLM strategies
    python3 build-strategies.py --strategy R2.1    # Build one strategy
    python3 build-strategies.py --dataset soong-v5 # Build one dataset
    python3 build-strategies.py --llm              # Also build LLM-dependent strategies
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STRATEGIES_DIR = PROJECT_ROOT / "strategies"
SOONG_SOURCE = PROJECT_ROOT / "soong-daystrom" / "_source-v5"
OBSIDIAN_SOURCE = PROJECT_ROOT / "test-datasets" / "obsidian"

DATASETS = {
    "soong-v5": SOONG_SOURCE,
    "obsidian": OBSIDIAN_SOURCE,
}

# All strategies and whether they need LLM
STRATEGIES = {
    "R1":   {"llm": False, "category": "reference"},
    "R2.1": {"llm": False, "category": "reference"},
    "R2.2": {"llm": True,  "category": "reference"},
    "R2.3": {"llm": False, "category": "reference"},
    "R2.4": {"llm": True,  "category": "reference"},
    "R3":   {"llm": False, "category": "reference"},
    "R4":   {"llm": False, "category": "reference"},
    "I1":   {"llm": False, "category": "index"},
    "I2":   {"llm": True,  "category": "index"},
    "I3":   {"llm": True,  "category": "index"},
    "I4":   {"llm": True,  "category": "index"},
    "C1":   {"llm": False, "category": "combo"},
    "C2":   {"llm": True,  "category": "combo"},
    "C3":   {"llm": False, "category": "combo"},
}

BUILD_METRICS = {}


def get_md_files(source_dir: Path) -> list[Path]:
    """Get all .md files in a directory, sorted, excluding questions.json."""
    files = sorted(source_dir.rglob("*.md"))
    # Exclude any non-content files
    return [f for f in files if f.name != "questions.json"]


def relative_data_path(file_path: Path, source_dir: Path) -> str:
    """Get the data/... relative path for a file."""
    rel = file_path.relative_to(source_dir)
    return f"data/{rel}"


def extract_keywords_simple(text: str, top_n: int = 8) -> list[str]:
    """Extract keywords using simple TF approach (no dependencies)."""
    # Remove markdown formatting
    text = re.sub(r'```[\s\S]*?```', '', text)  # code blocks
    text = re.sub(r'#+ ', '', text)  # headings
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links
    text = re.sub(r'[|*_`~>-]', ' ', text)  # markdown chars
    text = re.sub(r'https?://\S+', '', text)  # URLs
    text = re.sub(r'\d{4}[-/]\d{2}[-/]\d{2}', '', text)  # dates

    # Tokenize
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Simple stopwords
    stopwords = {
        'the', 'and', 'for', 'are', 'was', 'were', 'been', 'being', 'have',
        'has', 'had', 'having', 'does', 'did', 'doing', 'will', 'would',
        'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'must',
        'that', 'this', 'these', 'those', 'with', 'from', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'each', 'every', 'both', 'all', 'any', 'few', 'more', 'most',
        'other', 'some', 'such', 'only', 'same', 'than', 'too', 'very',
        'just', 'about', 'also', 'then', 'when', 'where', 'what', 'which',
        'who', 'whom', 'how', 'why', 'not', 'but', 'its', 'his', 'her',
        'their', 'our', 'your', 'they', 'them', 'she', 'him', 'you', 'use',
        'used', 'using', 'example', 'see', 'file', 'files', 'new', 'like',
        'based', 'etc', 'one', 'two', 'first', 'make', 'get', 'set',
        'run', 'running', 'note', 'well', 'work', 'way', 'data', 'add',
    }

    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(top_n)]


def create_symlink(strategy_dir: Path, source_dir: Path):
    """Create data symlink in strategy directory."""
    link_path = strategy_dir / "data"
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    # Compute relative path from strategy_dir to source_dir
    rel_path = os.path.relpath(source_dir, strategy_dir)
    link_path.symlink_to(rel_path)


# ─── Strategy Builders ───────────────────────────────────────────────

def build_R1(strategy_dir: Path, source_dir: Path, dataset: str):
    """R1: Baseline — no CLAUDE.md, just data symlink."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)
    # No CLAUDE.md — that's the point


def build_R2_1(strategy_dir: Path, source_dir: Path, dataset: str):
    """R2.1: Whole-file @ refs, plain."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)
    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. Use them to answer questions.\n")
    for f in files:
        ref = relative_data_path(f, source_dir)
        lines.append(f"@{ref}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_R2_3(strategy_dir: Path, source_dir: Path, dataset: str):
    """R2.3: Whole-file @ refs + keywords."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)
    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. Keywords are listed after each file reference.\n")

    for f in files:
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        keywords = extract_keywords_simple(text)
        kw_str = ", ".join(keywords) if keywords else "general"
        lines.append(f"@{ref} — Keywords: {kw_str}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_R3(strategy_dir: Path, source_dir: Path, dataset: str):
    """R3: Hierarchical @ refs — CLAUDE.md → sub-indexes → files."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    # Group files by top-level directory
    files = get_md_files(source_dir)
    groups = defaultdict(list)
    for f in files:
        rel = f.relative_to(source_dir)
        top_dir = rel.parts[0] if len(rel.parts) > 1 else "_root"
        groups[top_dir].append(f)

    # Create sub-index directory
    sub_dir = strategy_dir / "sub-indexes"
    sub_dir.mkdir(exist_ok=True)

    # Write sub-index for each group
    main_lines = ["# Knowledge Base Index\n"]
    main_lines.append("This knowledge base is organized by topic. Each sub-index lists the files in that section.\n")

    for group_name in sorted(groups.keys()):
        group_files = groups[group_name]
        sub_file = sub_dir / f"{group_name}.md"

        sub_lines = [f"# {group_name.replace('-', ' ').title()}\n"]
        for f in sorted(group_files):
            ref = relative_data_path(f, source_dir)
            sub_lines.append(f"@{ref}")

        sub_file.write_text("\n".join(sub_lines) + "\n")
        main_lines.append(f"@sub-indexes/{group_name}.md")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(main_lines) + "\n")


def build_R4(strategy_dir: Path, source_dir: Path, dataset: str):
    """R4: Selective @ refs — only key/entry-point files."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    # Heuristic: select files that are likely important
    # - Larger files (more content = more likely to be substantive)
    # - Files with "index", "overview", "architecture", "summary" in name
    # - Top-level files
    scored = []
    for f in files:
        rel = f.relative_to(source_dir)
        text = f.read_text(errors='replace')
        word_count = len(text.split())
        score = word_count  # base score = word count

        name_lower = f.stem.lower()
        # Boost for important-sounding names
        for keyword in ['index', 'overview', 'architecture', 'summary', 'executive',
                        'plan', 'strategy', 'project', 'report', 'analysis']:
            if keyword in name_lower:
                score *= 2
                break

        # Boost for shallower paths (more likely entry points)
        depth = len(rel.parts)
        if depth == 1:
            score *= 1.5

        scored.append((score, f))

    # Take top ~15 files (or 10-15% of total, whichever is larger)
    n_select = max(15, len(files) // 7)
    scored.sort(reverse=True)
    selected = [f for _, f in scored[:n_select]]

    lines = ["# Key Knowledge Base Files\n"]
    lines.append(f"The following {len(selected)} files are the most important entry points in this knowledge base. ")
    lines.append("Other files exist in the data/ directory but these are the key references.\n")

    for f in sorted(selected, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        lines.append(f"@{ref}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_I1(strategy_dir: Path, source_dir: Path, dataset: str):
    """I1: Keyword index — index.md mapping file → keywords."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    index_lines = ["# Keyword Index\n"]
    index_lines.append("This index maps each file to its key topics and terms.\n")
    index_lines.append("| File | Keywords |")
    index_lines.append("|------|----------|")

    for f in sorted(files, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        keywords = extract_keywords_simple(text)
        kw_str = ", ".join(keywords) if keywords else "—"
        index_lines.append(f"| `{ref}` | {kw_str} |")

    (strategy_dir / "index.md").write_text("\n".join(index_lines) + "\n")

    # CLAUDE.md references the index
    claude_lines = [
        "# Knowledge Base with Keyword Index\n",
        "Use the keyword index to find relevant files, then read those files to answer questions.\n",
        "@index.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")


def build_C1(strategy_dir: Path, source_dir: Path, dataset: str):
    """C1: R2.1 + I1 — whole-file refs + keyword index."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    # Build keyword index (same as I1)
    files = get_md_files(source_dir)

    index_lines = ["# Keyword Index\n"]
    index_lines.append("This index maps each file to its key topics and terms.\n")
    index_lines.append("| File | Keywords |")
    index_lines.append("|------|----------|")
    for f in sorted(files, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        keywords = extract_keywords_simple(text)
        kw_str = ", ".join(keywords) if keywords else "—"
        index_lines.append(f"| `{ref}` | {kw_str} |")
    (strategy_dir / "index.md").write_text("\n".join(index_lines) + "\n")

    # CLAUDE.md: whole-file refs + index reference
    lines = ["# Content Files with Keyword Index\n"]
    lines.append("Use the keyword index to quickly identify relevant files. All files are listed below.\n")
    lines.append("@index.md\n")
    for f in sorted(files, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        lines.append(f"@{ref}")
    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_C3(strategy_dir: Path, source_dir: Path, dataset: str):
    """C3: R3 + I1 — hierarchical refs + keyword index."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    # Build keyword index
    index_lines = ["# Keyword Index\n"]
    index_lines.append("| File | Keywords |")
    index_lines.append("|------|----------|")
    for f in sorted(files, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        keywords = extract_keywords_simple(text)
        kw_str = ", ".join(keywords) if keywords else "—"
        index_lines.append(f"| `{ref}` | {kw_str} |")
    (strategy_dir / "index.md").write_text("\n".join(index_lines) + "\n")

    # Build hierarchical sub-indexes (same as R3)
    groups = defaultdict(list)
    for f in files:
        rel = f.relative_to(source_dir)
        top_dir = rel.parts[0] if len(rel.parts) > 1 else "_root"
        groups[top_dir].append(f)

    sub_dir = strategy_dir / "sub-indexes"
    sub_dir.mkdir(exist_ok=True)

    main_lines = ["# Knowledge Base — Hierarchical Index with Keywords\n"]
    main_lines.append("Use the keyword index for topic search. Sub-indexes organize files by section.\n")
    main_lines.append("@index.md\n")

    for group_name in sorted(groups.keys()):
        group_files = groups[group_name]
        sub_file = sub_dir / f"{group_name}.md"
        sub_lines = [f"# {group_name.replace('-', ' ').title()}\n"]
        for f in sorted(group_files):
            ref = relative_data_path(f, source_dir)
            sub_lines.append(f"@{ref}")
        sub_file.write_text("\n".join(sub_lines) + "\n")
        main_lines.append(f"@sub-indexes/{group_name}.md")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(main_lines) + "\n")


# ─── LLM Helpers ────────────────────────────────────────────────────

LLM_CALL_COUNT = 0
LLM_TOTAL_COST = 0.0

def get_anthropic_client():
    """Lazy-load anthropic client."""
    try:
        import anthropic
        return anthropic.Anthropic()
    except ImportError:
        print("ERROR: anthropic SDK not installed. Run: pip install anthropic")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not create Anthropic client: {e}")
        sys.exit(1)


def llm_call(prompt: str, content: str, max_tokens: int = 300) -> str:
    """Call Haiku to generate text. Returns response text."""
    global LLM_CALL_COUNT, LLM_TOTAL_COST
    client = get_anthropic_client()

    # Truncate content to avoid huge prompts (keep first ~8K words)
    words = content.split()
    if len(words) > 8000:
        content = " ".join(words[:8000]) + "\n\n[truncated]"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": f"{prompt}\n\n---\n\n{content}"}],
    )

    LLM_CALL_COUNT += 1
    # Estimate cost: Haiku input ~$0.80/MTok, output ~$4/MTok
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (input_tokens * 0.80 + output_tokens * 4.0) / 1_000_000
    LLM_TOTAL_COST += cost

    text = response.content[0].text.strip()
    time.sleep(0.5)  # Rate limiting
    return text


def llm_summarize(content: str, sentences: int = 1) -> str:
    """Generate a summary of a document."""
    prompt = (
        f"Summarize the following document in exactly {sentences} sentence(s). "
        f"Focus on what the document is about, who/what it covers, and key facts. "
        f"Be specific — include names, numbers, and concrete details. "
        f"Return ONLY the summary sentence(s), no preamble."
    )
    return llm_call(prompt, content, max_tokens=150 * sentences)


# ─── LLM-Dependent Strategy Builders ────────────────────────────────

def build_R2_2(strategy_dir: Path, source_dir: Path, dataset: str):
    """R2.2: Whole-file @ refs + 1-sentence summary."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)
    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. One-sentence summaries describe each file.\n")

    for i, f in enumerate(files):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        summary = llm_summarize(text, sentences=1)
        lines.append(f"@{ref} — {summary}")
        if (i + 1) % 20 == 0:
            print(f"    R2.2: {i+1}/{len(files)} files summarized")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_R2_4(strategy_dir: Path, source_dir: Path, dataset: str):
    """R2.4: Whole-file @ refs + 2-sentence summary."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)
    lines = ["# Content Files\n"]
    lines.append("The following files contain the knowledge base. Two-sentence summaries describe each file.\n")

    for i, f in enumerate(files):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        summary = llm_summarize(text, sentences=2)
        lines.append(f"@{ref} — {summary}")
        if (i + 1) % 20 == 0:
            print(f"    R2.4: {i+1}/{len(files)} files summarized")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_I2(strategy_dir: Path, source_dir: Path, dataset: str):
    """I2: Relationship graph — connections between files."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    # Step 1: Get topics/entities for each file (LLM)
    file_topics = {}
    for i, f in enumerate(files):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        prompt = (
            "List the 3-5 main topics, entities, or concepts in this document. "
            "Return as a comma-separated list. Be specific (use names, products, etc). "
            "Return ONLY the list, no preamble."
        )
        topics = llm_call(prompt, text, max_tokens=100)
        file_topics[ref] = [t.strip() for t in topics.split(",")]
        if (i + 1) % 20 == 0:
            print(f"    I2: {i+1}/{len(files)} files analyzed for topics")

    # Step 2: Build relationship index by finding shared topics
    rel_lines = ["# File Relationship Graph\n"]
    rel_lines.append("This graph shows connections between files based on shared topics.\n")

    # Index topics → files
    topic_to_files = defaultdict(list)
    for ref, topics in file_topics.items():
        for topic in topics:
            topic_lower = topic.lower().strip()
            if topic_lower:
                topic_to_files[topic_lower].append(ref)

    # Only keep topics that connect 2+ files
    connections = {
        topic: refs for topic, refs in topic_to_files.items()
        if len(refs) >= 2
    }

    rel_lines.append(f"**{len(connections)} shared topics found across {len(files)} files.**\n")

    for topic in sorted(connections.keys()):
        refs = connections[topic]
        rel_lines.append(f"## {topic.title()}")
        for ref in sorted(refs):
            rel_lines.append(f"- `{ref}`")
        rel_lines.append("")

    (strategy_dir / "relationships.md").write_text("\n".join(rel_lines) + "\n")

    # CLAUDE.md
    claude_lines = [
        "# Knowledge Base with Relationship Graph\n",
        "Use the relationship graph to find connected files, then read those files to answer questions.\n",
        "@relationships.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")


def build_I3(strategy_dir: Path, source_dir: Path, dataset: str):
    """I3: Semantic grouping — files grouped by topic/feature."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    # Build a file listing with first ~100 words of each
    file_descriptions = []
    for f in files:
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        preview = " ".join(text.split()[:80])
        file_descriptions.append(f"- `{ref}`: {preview}")

    # Batch files for LLM grouping (process in chunks of ~40 files)
    chunk_size = 40
    all_groups = defaultdict(list)

    for start in range(0, len(file_descriptions), chunk_size):
        chunk = file_descriptions[start:start + chunk_size]
        chunk_text = "\n".join(chunk)

        prompt = (
            "Group these files by topic/capability. For each group, provide:\n"
            "GROUP: <group name>\n"
            "- `file/path`\n"
            "- `file/path`\n\n"
            "Use 4-8 meaningful groups. Return ONLY the grouped listing."
        )
        result = llm_call(prompt, chunk_text, max_tokens=2000)

        # Parse groups from result
        current_group = None
        for line in result.split("\n"):
            line = line.strip()
            if line.upper().startswith("GROUP:"):
                current_group = line.split(":", 1)[1].strip()
            elif line.startswith("- ") and current_group:
                # Extract file path from backticks or plain text
                match = re.search(r'`([^`]+)`', line)
                if match:
                    all_groups[current_group].append(match.group(1))

        print(f"    I3: Grouped files {start+1}-{min(start+chunk_size, len(files))}/{len(files)}")

    # Write capabilities.md
    cap_lines = ["# Knowledge Base — Semantic Groupings\n"]
    cap_lines.append(f"Files organized into {len(all_groups)} topic groups.\n")

    for group_name in sorted(all_groups.keys()):
        group_files = all_groups[group_name]
        cap_lines.append(f"## {group_name}")
        for ref in sorted(group_files):
            cap_lines.append(f"- `{ref}`")
        cap_lines.append("")

    (strategy_dir / "capabilities.md").write_text("\n".join(cap_lines) + "\n")

    # CLAUDE.md
    claude_lines = [
        "# Knowledge Base with Semantic Groupings\n",
        "Files are organized by topic. Use the groupings to find relevant files, then read them.\n",
        "@capabilities.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")


def build_I4(strategy_dir: Path, source_dir: Path, dataset: str):
    """I4: Summary index — 1-2 sentence summary per file."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    files = get_md_files(source_dir)

    sum_lines = ["# Summary Index\n"]
    sum_lines.append("Each file in the knowledge base with a brief summary.\n")
    sum_lines.append("| File | Summary |")
    sum_lines.append("|------|---------|")

    for i, f in enumerate(files):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        summary = llm_summarize(text, sentences=1)
        # Escape pipes in summary for table formatting
        summary = summary.replace("|", "\\|")
        sum_lines.append(f"| `{ref}` | {summary} |")
        if (i + 1) % 20 == 0:
            print(f"    I4: {i+1}/{len(files)} files summarized")

    (strategy_dir / "summaries.md").write_text("\n".join(sum_lines) + "\n")

    # CLAUDE.md
    claude_lines = [
        "# Knowledge Base with Summary Index\n",
        "Use the summary index to identify relevant files, then read them for details.\n",
        "@summaries.md",
    ]
    (strategy_dir / "CLAUDE.md").write_text("\n".join(claude_lines) + "\n")


def build_C2(strategy_dir: Path, source_dir: Path, dataset: str):
    """C2: R4 (selective refs) + I2 (relationship graph) combined."""
    strategy_dir.mkdir(parents=True, exist_ok=True)
    create_symlink(strategy_dir, source_dir)

    # Check if I2 was already built — reuse its relationships.md
    i2_dir = strategy_dir.parent / "I2"
    i2_rels = i2_dir / "relationships.md"

    if i2_rels.exists():
        # Copy relationship graph from I2
        import shutil
        shutil.copy2(i2_rels, strategy_dir / "relationships.md")
    else:
        # Build I2's relationship graph inline
        build_I2_relationships_only(strategy_dir, source_dir, dataset)

    # Build R4-style selective refs
    files = get_md_files(source_dir)
    scored = []
    for f in files:
        rel = f.relative_to(source_dir)
        text = f.read_text(errors='replace')
        word_count = len(text.split())
        score = word_count
        name_lower = f.stem.lower()
        for keyword in ['index', 'overview', 'architecture', 'summary', 'executive',
                        'plan', 'strategy', 'project', 'report', 'analysis']:
            if keyword in name_lower:
                score *= 2
                break
        depth = len(rel.parts)
        if depth == 1:
            score *= 1.5
        scored.append((score, f))

    n_select = max(15, len(files) // 7)
    scored.sort(reverse=True)
    selected = [f for _, f in scored[:n_select]]

    lines = ["# Key Files with Relationship Graph\n"]
    lines.append(f"The {len(selected)} most important files are listed below. ")
    lines.append("Use the relationship graph to discover connected files.\n")
    lines.append("@relationships.md\n")

    for f in sorted(selected, key=lambda x: x.relative_to(source_dir)):
        ref = relative_data_path(f, source_dir)
        lines.append(f"@{ref}")

    (strategy_dir / "CLAUDE.md").write_text("\n".join(lines) + "\n")


def build_I2_relationships_only(strategy_dir: Path, source_dir: Path, dataset: str):
    """Build just the relationships.md (used by C2 when I2 not yet built)."""
    files = get_md_files(source_dir)
    file_topics = {}
    for i, f in enumerate(files):
        ref = relative_data_path(f, source_dir)
        text = f.read_text(errors='replace')
        prompt = (
            "List the 3-5 main topics, entities, or concepts in this document. "
            "Return as a comma-separated list. Be specific. Return ONLY the list."
        )
        topics = llm_call(prompt, text, max_tokens=100)
        file_topics[ref] = [t.strip() for t in topics.split(",")]

    topic_to_files = defaultdict(list)
    for ref, topics in file_topics.items():
        for topic in topics:
            topic_lower = topic.lower().strip()
            if topic_lower:
                topic_to_files[topic_lower].append(ref)

    connections = {t: refs for t, refs in topic_to_files.items() if len(refs) >= 2}

    rel_lines = ["# File Relationship Graph\n"]
    rel_lines.append(f"**{len(connections)} shared topics across {len(files)} files.**\n")
    for topic in sorted(connections.keys()):
        refs = connections[topic]
        rel_lines.append(f"## {topic.title()}")
        for ref in sorted(refs):
            rel_lines.append(f"- `{ref}`")
        rel_lines.append("")

    (strategy_dir / "relationships.md").write_text("\n".join(rel_lines) + "\n")


# ─── Dispatcher ──────────────────────────────────────────────────────

NON_LLM_BUILDERS = {
    "R1": build_R1,
    "R2.1": build_R2_1,
    "R2.3": build_R2_3,
    "R3": build_R3,
    "R4": build_R4,
    "I1": build_I1,
    "C1": build_C1,
    "C3": build_C3,
}

LLM_BUILDERS = {
    "R2.2": build_R2_2,
    "R2.4": build_R2_4,
    "I2": build_I2,
    "I3": build_I3,
    "I4": build_I4,
    "C2": build_C2,
}


def build_strategy(strategy: str, dataset: str, source_dir: Path, include_llm: bool = False):
    """Build a single strategy for a single dataset."""
    strategy_dir = STRATEGIES_DIR / dataset / strategy

    builders = {**NON_LLM_BUILDERS}
    if include_llm:
        builders.update(LLM_BUILDERS)

    if strategy not in builders:
        if strategy in STRATEGIES and STRATEGIES[strategy]["llm"] and not include_llm:
            print(f"  SKIP {strategy}/{dataset} (requires --llm)")
            return
        print(f"  SKIP {strategy}/{dataset} (no builder yet)")
        return

    start = time.time()
    calls_before = LLM_CALL_COUNT
    cost_before = LLM_TOTAL_COST
    builders[strategy](strategy_dir, source_dir, dataset)
    elapsed = time.time() - start
    calls_made = LLM_CALL_COUNT - calls_before
    cost_incurred = LLM_TOTAL_COST - cost_before

    # Count artifacts
    artifacts = list(strategy_dir.glob("*.md")) + list(strategy_dir.rglob("sub-indexes/*.md"))
    artifact_size = sum(f.stat().st_size for f in artifacts if f.is_file())

    BUILD_METRICS[f"{strategy}/{dataset}"] = {
        "strategy_id": strategy,
        "dataset": dataset,
        "index_build": {
            "method": "llm_assisted" if strategy in LLM_BUILDERS else "automated_nlp",
            "llm_calls": calls_made,
            "llm_cost_usd": round(cost_incurred, 4),
            "build_time_seconds": round(elapsed, 2),
            "artifact_count": len(artifacts),
            "artifact_size_bytes": artifact_size,
        }
    }

    print(f"  BUILT {strategy}/{dataset} ({len(artifacts)} artifacts, {artifact_size:,} bytes, {elapsed:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Build Phase 2 strategy folders")
    parser.add_argument("--strategy", help="Build only this strategy")
    parser.add_argument("--dataset", help="Build only this dataset")
    parser.add_argument("--llm", action="store_true", help="Include LLM-dependent strategies")
    parser.add_argument("--list", action="store_true", help="List all strategies")
    args = parser.parse_args()

    if args.list:
        print("\nPhase 2 Strategies:")
        print(f"{'ID':<8} {'Category':<12} {'LLM?':<6} {'Builder?'}")
        print("-" * 40)
        for sid, info in STRATEGIES.items():
            has_builder = sid in NON_LLM_BUILDERS or sid in LLM_BUILDERS
            print(f"{sid:<8} {info['category']:<12} {'Yes' if info['llm'] else 'No':<6} {'Ready' if has_builder else 'TODO'}")
        return

    STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {args.dataset: DATASETS[args.dataset]} if args.dataset else DATASETS
    strategies = [args.strategy] if args.strategy else list(STRATEGIES.keys())

    print(f"\nBuilding {len(strategies)} strategies × {len(datasets)} datasets")
    print(f"Output: {STRATEGIES_DIR}/\n")

    for dataset, source_dir in datasets.items():
        print(f"\n--- Dataset: {dataset} ({source_dir}) ---")
        if not source_dir.exists():
            print(f"  ERROR: Source directory not found: {source_dir}")
            continue

        for strategy in strategies:
            build_strategy(strategy, dataset, source_dir, include_llm=args.llm)

    # Write build metrics
    metrics_file = STRATEGIES_DIR / "build-metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(BUILD_METRICS, f, indent=2)

    print(f"\nBuild metrics written to {metrics_file}")
    print(f"Total strategies built: {len(BUILD_METRICS)}")
    if LLM_CALL_COUNT > 0:
        print(f"LLM calls: {LLM_CALL_COUNT}, estimated cost: ${LLM_TOTAL_COST:.4f}")


if __name__ == "__main__":
    main()
