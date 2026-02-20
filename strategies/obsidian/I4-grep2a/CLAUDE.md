# Knowledge Base

This directory contains a knowledge base of files in the `data/` folder.
A summary index with one-line descriptions of every file is at `summaries.md`.

## How to find relevant files

Search the summary index using Grep:

```
grep -iE "keyword1|keyword2" summaries.md
```

Replace `keyword1`, `keyword2` with terms from the question. This returns matching rows with file paths and descriptions.

Then Read the matched data files to answer the question.
