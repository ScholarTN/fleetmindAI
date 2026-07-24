import uuid
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.ai.vector_store import add_documents

DOCUMENTS_PATH = Path("data/documents")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""],
)


def extract_pdf(pdf_path: Path) -> str:
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def ingest_pdf(pdf_path: Path):
    print(f"Ingesting {pdf_path.name}")

    text = extract_pdf(pdf_path)

    chunks = text_splitter.split_text(text)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(str(uuid.uuid4()))
        documents.append(chunk)
        metadatas.append(
            {
                "source": pdf_path.name,
                "chunk": i,
            }
        )

    add_documents(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Stored {len(chunks)} chunks")


def ingest_all():
    pdfs = list(DOCUMENTS_PATH.glob("*.pdf"))

    if not pdfs:
        print("No PDFs found.")
        return

    for pdf in pdfs:
        ingest_pdf(pdf)

    print("Knowledge base ready.")


if __name__ == "__main__":
    ingest_all()