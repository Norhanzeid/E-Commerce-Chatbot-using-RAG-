import os

# Avoid Windows symlink permission errors (WinError 1314) when huggingface_hub caches models
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from langchain_core.documents import Document

####################### INGESTION SCRIPT ########################

# Source documents are read from data/raw/ so the project is portable across machines
RAW_DATA_DIR = os.path.join("data", "raw")

# OCR is enabled so text inside embedded images/screenshots/figures is extracted.
# force_full_page_ocr=False keeps this hybrid/layout-aware: pages with a reliable
# native text layer keep that text as-is, and OCR only runs on bitmap/picture
# regions (e.g. screenshots) that have no selectable text, then Docling merges
# both into a single reading-order text stream (native text + OCR text combined).
_pdf_options = PdfPipelineOptions()
_pdf_options.do_ocr = True
_pdf_options.ocr_options.force_full_page_ocr = False
_pdf_options.do_table_structure = True
_pdf_options.generate_picture_images = True


def _make_pdf_converter():
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=_pdf_options)}
    )


def ingest_documents():

    """Ingest TXT and PDF files, chunk them,Then embedding and save to FAISS vector database."""
    
    # Create directory for vector database

    os.makedirs("data/vector_db", exist_ok=True)

    if not os.path.isdir(RAW_DATA_DIR):
        print(f"Source folder not found: {RAW_DATA_DIR}. Create it and add your TXT/PDF files.")
        return
    
    documents = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    # ----------- Load all TXT files in data/raw -----------

    txt_files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith(".txt")]
    for txt_name in txt_files:
        print(f"Loading TXT file ({txt_name})...")
        try:
            txt_path = os.path.join(RAW_DATA_DIR, txt_name)
            txt_loader = TextLoader(txt_path, encoding="utf8")
            txt_docs = txt_loader.load()
            txt_chunks = splitter.split_documents(txt_docs)
            documents.extend(txt_chunks)
            print(f"TXT loaded: {len(txt_chunks)} chunks created")

        except Exception as e:
            print(f"Error loading TXT ({txt_name}): {e}")

    # ----------- Load all PDF files in data/raw using Docling -----------

    pdf_files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith(".pdf")]
    for pdf_name in pdf_files:
        print(f"Loading PDF ({pdf_name})...")
        try:
            pdf_path = os.path.join(RAW_DATA_DIR, pdf_name)
            converter = _make_pdf_converter()
            result = converter.convert(pdf_path)

            # Split by page so each chunk keeps a page-number for citation/debugging
            page_marker = "\x00PAGE\x00"
            pages_markdown = result.document.export_to_markdown(page_break_placeholder=page_marker).split(page_marker)

            page_docs = [
                Document(page_content=page_text, metadata={"source": pdf_name, "page": page_num})
                for page_num, page_text in enumerate(pages_markdown, start=1)
                if page_text.strip()
            ]
            pdf_chunks = splitter.split_documents(page_docs)
            documents.extend(pdf_chunks)
            print(f"PDF loaded: {len(pdf_chunks)} chunks created ({len(page_docs)} pages)")

        except Exception as e:
            print(f"Error loading PDF ({pdf_name}): {e}")

    # ----------- Create Vector DB -----------
    if not documents:
        print("No documents to process!")
        return
    
    ##################### Create Embeddings and Vector DB #####################

    print(f"\n Creating embeddings for {len(documents)} total chunks...")

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Building FAISS vector database...")
    vector_db = FAISS.from_documents(documents, embedding)
    vector_db.save_local("data/vector_db")

    print(f"\n Ingestion Completed Successfully!")
    print(f"   Total chunks: {len(documents)}")
    print(f"   Saved to: data/vector_db")
    print(f"\n Summary:")
    print(f"   - Combined all TXT and PDF files into single vector database")
    print(f"   - Ready for semantic search and question answering")


if __name__ == "__main__":
    ingest_documents()

