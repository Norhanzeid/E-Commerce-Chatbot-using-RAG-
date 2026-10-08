# ShopSphere Insight

**A document-grounded business intelligence assistant for the ShopSphere FY2025 report.**

ShopSphere Insight is a local Streamlit chat application built with retrieval-augmented generation (RAG). It indexes PDF and plain-text business documents, finds relevant passages for a question, and asks an OpenAI chat model to answer using those passages as its source.

## Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Add or update knowledge-base documents](#add-or-update-knowledge-base-documents)
- [Run the application](#run-the-application)
- [Ask useful questions](#ask-useful-questions)
- [Project layout](#project-layout)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Privacy and limitations](#privacy-and-limitations)

## Features

- Chat-style Streamlit interface with a conversation history for the current session.
- PDF and UTF-8 text ingestion from `data/raw/`.
- OCR-enabled PDF processing with Docling, including table structure extraction and page-aware chunks.
- Local semantic embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
- FAISS similarity search over the generated document index.
- OpenAI answer generation using retrieved text as context.
- Prompt rules that discourage unsupported claims and restrict answers to the ShopSphere knowledge base.

## How it works

1. `ingest.py` reads `.pdf` and `.txt` files in `data/raw/`.
2. PDF files are converted to Markdown by Docling, with OCR enabled. Text is split into overlapping chunks of up to 1,000 characters.
3. The Hugging Face sentence-transformer model embeds the chunks, and FAISS saves the index under `data/vector_db/`.
4. When a question is submitted, `retriever.py` loads the FAISS index and returns the six most similar chunks by default.
5. `generator.py` sends the question and retrieved context to the OpenAI chat completions API (default model: `gpt-4o-mini`).
6. `main.py` displays the answer in the Streamlit chat interface.

The vector index and source documents are local project data. They are not included in Git.

## Requirements

- Python 3.10 or newer.
- An OpenAI API key with access to the configured chat model.
- An internet connection for installing packages, downloading the embedding model the first time, and making OpenAI API requests.
- Enough disk space and memory for Docling, PyTorch, the embedding model, and the document index. PDF OCR can take time.

## Quick start

Run these commands from the repository root in PowerShell:

```powershell
# Create and activate a virtual environment
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the project dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Create the local API-key file
Copy-Item .env.example .env
```

Open `.env` in a text editor and set your key:

```env
OPENAI_API_KEY=your_openai_api_key
```

If PowerShell blocks virtual-environment activation, you can invoke the environment's Python and Streamlit executables directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run main.py
```

Before running the app for the first time, add at least one supported source document and build the index as described below.

## Add or update knowledge-base documents

1. Create the source directory if it does not exist:

   ```powershell
   New-Item -ItemType Directory -Force data\raw
   ```

2. Put one or more `.pdf` or `.txt` files in `data/raw/`. For example:

   ```text
   data/
   └── raw/
       ├── ShopSphere_FY2025_BI_Report.pdf
       └── supplemental_notes.txt
   ```

3. Run ingestion from the repository root:

   ```powershell
   python ingest.py
   ```

   A successful run reports the number of chunks and saves the FAISS files in `data/vector_db/`. The first run may download the embedding model.

4. Re-run `python ingest.py` after adding, removing, or changing source documents. The index is built from the supported files currently present in `data/raw/`.

The index needs to exist before the app can answer questions. If ingestion reports that there are no documents to process, check that the files are in `data/raw/` and have a `.pdf` or `.txt` extension.

## Run the application

From the repository root, with the virtual environment activated and the index prepared:

```powershell
python -m streamlit run main.py
```

Streamlit prints a local URL (usually `http://localhost:8501`) in the terminal and typically opens it in your browser. Enter a question about the indexed ShopSphere business documents and select **Search**. The chat history is held in Streamlit session state and starts over in a new session.

To stop the app, press `Ctrl+C` in the terminal where it is running.

## Ask useful questions

Use specific questions that refer to information likely to appear in the source documents. For example:

- What was ShopSphere's FY2025 GMV?
- Which channels drove the strongest margin improvements?
- What were the main operating cost drivers?
- How did fulfillment costs affect profitability?

The assistant can combine relevant retrieved passages, but its answer quality depends on the documents that were successfully extracted and indexed. It may say it does not have enough information when the index does not contain relevant evidence.

## Project layout

```text
.
├── main.py             # Streamlit chat application
├── generator.py        # Prompt construction and OpenAI answer generation
├── retriever.py        # FAISS loading and similarity search
├── ingest.py           # PDF/TXT loading, chunking, embeddings, and index creation
├── requirements.txt    # Python package dependencies
├── .env.example        # Environment-variable template
└── data/
    ├── raw/            # Your source PDF and TXT files (local, not committed)
    └── vector_db/      # Generated FAISS index (local, not committed)
```

## Configuration

| Setting | Location | Default | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | `.env` | Required | API key used by the OpenAI client. |
| Chat model | `generator.py` | `gpt-4o-mini` | Model used to generate answers. |
| Retrieved chunks | `main.py` | `k=6` | Number of relevant passages added to the answer context. |
| Embedding model | `ingest.py`, `retriever.py` | `sentence-transformers/all-MiniLM-L6-v2` | Model used to embed source chunks and search queries. |
| Chunk size / overlap | `ingest.py` | 1,000 / 150 characters | Text splitting settings applied before indexing. |

Keep the embedding model consistent between ingestion and retrieval. If you change it, rebuild the index with `python ingest.py`.

## Troubleshooting

### `OPENAI_API_KEY not found in .env file!`

Confirm that `.env` exists in the project root, uses the exact variable name `OPENAI_API_KEY`, and contains a valid key. Restart Streamlit after changing the file. Do not add `.env` to Git.

### FAISS index or index files cannot be found

Run `python ingest.py` from the repository root and confirm that it completed successfully and created files in `data/vector_db/`. The app does not build the index automatically.

### `data/raw/` is empty or missing

Create `data/raw/` and add PDF or TXT source files, then run ingestion again. Files and folders under `data/` are intentionally excluded from the repository.

### PDF ingestion fails or takes a long time

Docling's PDF conversion and OCR are resource-intensive. Check that the PDF opens correctly, allow the first model downloads to finish, and inspect the ingestion output for the filename and error. Text-based PDFs may process faster than scanned documents.

### Answers are incomplete or incorrect

Check that the source file was included during ingestion, rebuild the index after modifying it, and ask a more specific question. Retrieval-augmented generation can still miss context or produce errors; verify important business decisions against the original report.

## Privacy and limitations

- Source documents, extracted chunks, and the FAISS index are stored locally and are not committed to this repository.
- The user's question and retrieved text are included in the request to OpenAI for answer generation. Do not index or query sensitive information unless its use with the configured API service is permitted.
- The embedding model may be downloaded from Hugging Face the first time it is used.
- The application is configured around ShopSphere business-report questions. Its prompt instructs the model not to answer unrelated questions or invent unsupported facts, but prompts cannot guarantee that every answer is correct.
- Retrieved results are not presented as formal citations in the current interface.
- OpenAI usage may incur charges and is subject to API availability, rate limits, and the account's model access.
- Only process FAISS index files you trust. The retriever uses LangChain's dangerous-deserialization option to load the locally generated index.
