# 🔬 DataLens — Smart Document & Data Analyst

> A fully local AI system that lets you interact with PDF documents and CSV datasets using natural language. No API costs. No data leaves your machine.

---

## What It Does

DataLens combines two powerful pipelines into one unified interface:

- **Ask questions about PDF documents** → get grounded answers with source references
- **Analyze CSV datasets** → get text insights and auto-generated charts

---

## Features

### 📄 PDF Question Answering (RAG)
- Upload any PDF document
- Automatically chunks and embeds document content
- Retrieves relevant context using semantic search
- Answers grounded strictly in document content
- Shows source chunks used for transparency

### 📊 CSV Data Analysis
- Upload any CSV dataset
- Automatically handles null values
- Answer questions about trends, averages, totals, counts
- Auto-generates bar, line, and histogram charts
- Natural language insights with specific numbers

### 🔀 Intelligent Routing
- Automatically detects file type (PDF or CSV)
- Routes to the correct pipeline without user configuration
- Detects chart intent from natural language keywords

### 🔒 Local First
- Runs 100% on your machine
- Uses Ollama for LLM and embeddings
- No OpenAI, no API keys, no subscription costs
- Complete data privacy

---

## Demo

### PDF Question Answering
```
Upload: c_programming.pdf
You: What is a token in C?
Bot: A token is the smallest individual unit of a C program.
     Every instruction in a C program is a collection of tokens...
     
     Sources: [Chunk 1] [Chunk 2] [Chunk 3]
```

### CSV Analysis
```
Upload: Orders_2025-10.csv
You: What is the average unit price by department?
Bot: IT department leads with an average unit price of 52.14,
     while HR has the lowest at 38.91...
     [Chart generated]

You: Show total units sold over orderdate
Bot: Units sold peaked in mid-October with a clear upward trend...
     [Line chart generated]
```

---

## Architecture

```
User Input (Question + File)
          │
          ▼
    File Type Detection
          │
    ┌─────┴──────┐
    ▼            ▼
  PDF          CSV
    │            │
    ▼            ▼
Chunking     Load + Clean
Embedding    Null Handling
Vector DB         │
Retrieval         ▼
    │        LLM decides
    │        operation
    │             │
    │        Pandas executes
    │             │
    │        Chart generation
    │             │
    └─────┬───────┘
          ▼
   Answer + Sources / Chart
          │
          ▼
     Streamlit UI
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Ollama (Mistral 7B) |
| Embeddings | Ollama (nomic-embed-text) |
| Vector Database | ChromaDB |
| RAG Framework | LangChain |
| Data Processing | pandas |
| Visualization | matplotlib / seaborn |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/datalens.git
cd datalens
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Pull Required Models
```bash
ollama pull mistral
ollama pull nomic-embed-text
```

### 5. Run the App
```bash
cd app
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Usage

### PDF Documents
1. Upload any PDF using the sidebar
2. Ask questions in plain English
3. View answers with source chunk references

**Example questions:**
```
"What is the main topic of this document?"
"Summarize the key findings"
"What does the document say about X?"
```

### CSV Datasets
1. Upload any CSV file using the sidebar
2. Check available columns in the sidebar expander
3. Ask analytical or visual questions

**Example text questions:**
```
"What is the average unit price?"
"Which department has the highest total sales?"
"What is the maximum discount rate?"
```

**Example chart questions:**
```
"Show total units sold by region"
"Plot average unit price by department"
"Show distribution of unit prices"
"Show total units sold over orderdate"
```

---

## Key Concepts Demonstrated

- **Retrieval Augmented Generation (RAG)** — grounding LLM answers in document content
- **Text chunking and embedding** — splitting documents for efficient retrieval
- **Vector similarity search** — finding relevant content by meaning not keywords
- **Prompt engineering** — structured LLM outputs for reliable parsing
- **Agentic decision making** — LLM decides what operation to perform
- **Pandas + LLM integration** — LLM thinks, pandas calculates, LLM explains
- **End-to-end AI system design** — from raw file to natural language answer

---

## Limitations

- Runs on CPU — responses take 20-50 seconds depending on hardware
- PDF answers depend on chunking quality and embedding accuracy
- CSV analysis limited to single file operations
- LLM may misinterpret ambiguous column names
- Large PDFs (50+ pages) may produce slower retrieval
- No multi-document support in current version

---

## Future Improvements

- [ ] Conversation memory for follow-up questions
- [ ] Multi-document PDF support
- [ ] Reranking for improved RAG retrieval quality
- [ ] More chart types (scatter, pie, heatmap)
- [ ] Export chat history as PDF report
- [ ] Voice input interface
- [ ] Support for Excel (.xlsx) files
- [ ] GPU acceleration for faster inference

---

## Why This Project

Most RAG demos only handle one type of data. DataLens handles both unstructured documents and structured datasets in a unified interface — demonstrating practical AI system design skills:

- Routing logic between pipelines
- Robust validation and error handling
- Local-first architecture for privacy
- Production-ready code structure

---

## Author

Built as a portfolio project demonstrating end-to-end AI system design using local models.

---

