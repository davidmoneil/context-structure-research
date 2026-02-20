# Knowledge Base

This directory contains a knowledge base of files in the `data/` folder.

## How to find relevant files

Run the search script with keywords from the question:

```bash
./search-index.sh keyword1 keyword2
```

This searches `summaries.md` and returns matching file paths with descriptions. Then Read the matched data files to answer the question.

Example: `./search-index.sh budget revenue` returns all files about budgets and revenue.
