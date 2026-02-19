---
created: 2025-06-01T22:53
modified: 2025-06-07T18:40
tags:
  - project/aiprojects
  - depth/deep
  - domain/ai
  - depth/standard
  - domain/infrastructure
updated: 2026-01-24T10:59
---



## Getting Documents Into RAG 
Step 1 [📃 Document - 🤖 AI Process Workflow Step 1](https://n8n.cisoexpert.synology.me/workflow/jT1Ln3SZXbNxqjJd)
- Successfully Parses Tabs of Excel Files 
- Task - need to put it into the database 
Fix the meta data to not be a sub metadata


Step 2 [📃 Document - 🤖 AI Process Workflow Step 2 (Set File Meta Data)](https://n8n.cisoexpert.synology.me/workflow/2Z6hYxS1HkIq1wGR) (Good) 


## Database 
1. documents
	1. match_documents Functions 
	2. 
2. document_metadata
	1. Should just be the meta data? 
3. document_rows


## Examples 
Testing - Get Obsidian Files [Agentic RAG w/ Obsidian Template](https://n8n.cisoexpert.synology.me/workflow/oq1JwaC9ezaflgJU)
- How to 

Example from Cole - [Example - 🚀 n8n Local AI Agentic RAG Template](https://n8n.cisoexpert.synology.me/workflow/jkXkInl6Oy59FHpY)
- Uses SupaBase, to access Functions defined in Postgres through the Storage tool in SupaBase, postgres doesn't have one. 
- [Postgres-Database_Function_Call](https://n8n.cisoexpert.synology.me/workflow/TigPFXATe8atBXH7)
	- Not working correctly 
	- 
- 

# How to use the data 
https://gemini.google.com/app/baa3148ced59370f
Okay, let's break down this n8n workflow and its interaction with your PostgreSQL database.

This workflow is designed to create an **Agentic RAG (Retrieval Augmented Generation)** system. It ingests documents from Google Drive, processes them (extracts text, chunks it, creates vector embeddings for text, and stores tabular data), and then allows an AI agent to answer questions using this knowledge base. The agent can decide whether to use semantic search (RAG) over text, query tabular data using SQL, or retrieve full document content.

Here's how it interacts with PostgreSQL and an explanation of your tables:

---

## 1. How to Think About `documents`, `document_metadata`, and `document_rows`

These three tables form the core of your knowledge base:

- **`document_metadata` Table:**
    
    - **Purpose:** This is your master catalog of all ingested files. Think of it as the librarian knowing which books (files) are in the library.
    - **Content:**
        - `id`: The unique ID of the file (e.g., Google Drive file ID). This is the **PRIMARY KEY**.
        - `title`: The name/title of the file.
        - `url`: A link to the original file.
        - `created_at`: Timestamp of when the record was created.
        - `schema`: If the file is tabular (CSV/Excel), this field stores the column headers (schema) of that table as a JSON string. This is populated by the "Update Schema for Document Metadata" node.
    - **Interaction:**
        - Populated by "Insert Document Metadata" when a new file is processed.
        - Updated by "Update Schema for Document Metadata" if the file is tabular.
        - Queried by the "List Documents" AI tool to let the agent know what files and their schemas are available.
- **`documents` Table:**
    
    - **Purpose:** This table stores the **text content** (often in chunks) from your documents and their corresponding **vector embeddings**. This is primarily used for semantic search (RAG). The `document.PageContent` you mentioned in the prompt (likely from LangChain terminology) corresponds to the `content` column in this table.
    - **Content:**
        - `id`: A unique identifier for each chunk/document segment (auto-incrementing `bigserial`).
        - `content`: The actual text chunk.
        - `metadata`: A JSONB field storing metadata about the chunk, critically including the `file_id` and `file_title` of the original document from which the chunk was derived. This links back to `document_metadata`. (See "Default Data Loader" node parameters).
        - `embedding`: The vector embedding (e.g., from OpenAI's `text-embedding-3-small`) for the `content` field.
    - **Interaction:**
        - Populated by the "Insert into Supabase Vectorstore" node after files are downloaded, text extracted (e.g., "Extract PDF Text," "Extract Document Text"), chunked (implicitly by "Default Data Loader" or explicitly if a text splitter was placed before it), and embedded (by "Embeddings OpenAI1").
        - Queried by the "Supabase Vector Store1" node (configured as an AI tool named "documents") using the `match_documents` function for semantic search. This function takes a query embedding and returns similar document chunks.
        - Queried by the "Get File Contents" AI tool to retrieve all text content for a specific `file_id`.
        - Rows are deleted by "Delete Old Doc Rows" when a source file is updated/deleted to prevent stale data.
- **`document_rows` Table:**
    
    - **Purpose:** This table is specifically for storing the **raw row-by-row data from tabular files** (CSVs, Excel spreadsheets).
    - **Content:**
        - `id`: Auto-incrementing primary key for each row entry.
        - `dataset_id`: The `file_id` of the tabular document this row belongs to. This is a **FOREIGN KEY** referencing `document_metadata.id`.
        - `row_data`: A JSONB field containing the actual data of one row from the spreadsheet (e.g., `{"column1": "value1", "column2": "value2"}`).
    - **Interaction:**
        - Populated by the "Insert Table Rows" node. Each item processed by this node is one row from the extracted Excel or CSV file.
        - Queried by the "Query Document Rows" AI tool, which allows the AI agent to execute SQL queries directly against this structured data (e.g., for aggregations, specific lookups based on cell values).
        - Rows are deleted by "Delete Old Data Rows" when the corresponding source file is updated/deleted.

---

## 2. Where to Store Text vs. Vectors?

- **Text (for semantic search):** Stored in the **`content` column of the `documents` table**. This is typically chunked text.
- **Vectors:** Stored in the **`embedding` column of the `documents` table**. Each vector corresponds to the text in the `content` column of the same row.
- **Text (raw tabular data):** Stored as JSONB in the **`row_data` column of the `document_rows` table**. This is the original cell content from spreadsheets.
- **Text (metadata):** File titles, URLs, and tabular schemas are stored as text in the **`document_metadata` table**.

---

## 3. How to Use `documents` vs. `document_metadata`?

- Use **`document_metadata`** to:
    
    - Get a list of all available files and their general information (title, type via URL or schema).
    - Allow the AI agent to understand what documents exist in the knowledge base ("List Documents" tool).
    - For tabular data, to retrieve the `schema` so the AI knows what columns it can query in the `document_rows` table.
- Use **`documents`** to:
    
    - Perform **semantic search (RAG)**. The AI agent sends a query, it's embedded, and the `match_documents` function finds the most relevant text chunks from the `content` column by comparing query embedding with stored `embedding`s ("Supabase Vector Store1" tool).
    - Retrieve the full (or aggregated chunked) **text content** of a specific document if the agent decides it needs more than just RAG snippets ("Get File Contents" tool). The `metadata` field within `documents` (containing `file_id`) is key to linking these chunks back to an entry in `document_metadata`.

---

## 4. Where Does the Filter Get Applied?

Filters are applied in several places:

1. **Semantic Search (`match_documents` function):**
    
    - The `match_documents` PostgreSQL function, which is called by the "Supabase Vector Store1" tool, has a `filter JSONB DEFAULT '{}'` parameter.
    - The SQL for this function includes `WHERE metadata @> filter`. This means you can pass a JSON object to this function, and it will only consider rows in the `documents` table where the `metadata` column contains all the key-value pairs from your filter. For example, if your `documents.metadata` column stores `{"file_id": "xyz", "category": "report"}`, you could filter to only search within documents where `file_id` is 'xyz'. The "Default Data Loader" node adds `file_id` and `file_title` to this metadata.
2. **Deleting Old Document Chunks ("Delete Old Doc Rows"):**
    
    - This Supabase node (which interacts with Postgres) uses `filterString: "=metadata->>file_id=like.*{{ $json.file_id }}*"` to delete rows from the `documents` table. It targets rows where the `file_id` in the `metadata` JSONB column matches the `file_id` of the file being processed (e.g., if the file was updated). _(Note: `like.*...*` for an ID is unusual; typically `eq` or `=` would be used for an exact ID match. The current setup might be broader than intended or Supabase has specific syntax here, but the intent is to filter by `file_id` within the JSONB.)_
3. **Deleting Old Tabular Data ("Delete Old Data Rows"):**
    
    - This Supabase node deletes rows from the `document_rows` table. It uses the `filters` parameter: `{"keyName": "dataset_id", "condition": "eq", "keyValue": "={{ $('Set File ID').item.json.file_id }}"}`. This translates to a SQL `WHERE dataset_id = 'your_file_id'`.
4. **SQL Queries on Tabular Data ("Query Document Rows" tool):**
    
    - When the AI uses the "Query Document Rows" tool, it generates a SQL query. Filters are applied directly within that SQL query using `WHERE` clauses. For example: `SELECT AVG((row_data->>'revenue')::numeric) FROM document_rows WHERE dataset_id = '123' AND row_data->>'category' = 'Electronics';` Here, `dataset_id = '123'` and `row_data->>'category' = 'Electronics'` are filters.

In essence, the workflow is quite sophisticated, allowing the AI to dynamically choose the best way to access information based on the nature of the question and the type of data available.