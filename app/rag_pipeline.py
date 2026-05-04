from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os


llm = ChatOllama(model="mistral", temperature=0.1)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
conversation_history = []
vectorstore = None

# Load PDF


def load_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n\n"
    return full_text


# chunk text
def chunk_text(full_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    return text_splitter.create_documents([full_text])


def build_knowledge_base(pdf_path, chroma_dir, force_rebuild=False):
    global vectorstore

    if os.path.exists(chroma_dir) and os.listdir(chroma_dir) and not force_rebuild:
        vectorstore = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings,
        )

        print("Knowledge base loaded from disk")
        return

    full_text = load_pdf(pdf_path)
    chunks = chunk_text(full_text)
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=chroma_dir
    )
    print(f"Knowledge base built: {len(chunks)} chunks")


# retrieve relevant chunks
def retrieve(question):
    k = 5 if len(question.split()) > 10 else 3

    results = vectorstore.similarity_search_with_relevance_scores(question, k=k)

    THRESHOLD = 0.3
    filtered = [(doc, score) for doc, score in results if score >= THRESHOLD]
    return filtered


def ask(question):
    retrieved = retrieve(question)

    if not retrieved:
        return "I could not find relevant information in the document.", []

    context = "\n\n".join([doc.page_content for doc, score in retrieved])
    source_chunks = [doc for doc, score in retrieved]

    recent_history = conversation_history[-6:]

    messages = (
        [
            SystemMessage(
                content=f"""You are a helpful assistant.
        Answer using ONLY the context below.
        If the answer is not in the context, say 'I dont know based on the document'.
        CONTEXT:
        {context}"""
            )
        ]
        + recent_history
        + [HumanMessage(content=question)]
    )

    response = llm.invoke(messages)
    answer = response.content

    conversation_history.append(HumanMessage(content=question))
    conversation_history.append(AIMessage(content=answer))

    return answer, source_chunks


def clear_history():
    conversation_history.clear()
    print("Memory cleared.")
