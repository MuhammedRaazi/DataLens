import streamlit as st
import os
import pandas as pd
from router import route

st.set_page_config(page_title="DataLens", page_icon="🔬", layout="wide")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def init_session():
    defaults = {
        "messages": [],
        "file_path": None,
        "file_name": None,
        "df_columns": None,
        "file_type": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def save_file(uploaded_file):
    path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/data-configuration.png", width=60)
        st.title("DataLens")
        st.caption("Smart Document & Data Analyst")
        st.divider()

        uploaded_file = st.file_uploader(
            "Upload File",
            type=["pdf", "csv"],
            help="Supports PDF documents and CSV datasets",
        )

        if uploaded_file:
            if uploaded_file.name != st.session_state.file_name:
                path = save_file(uploaded_file)
                st.session_state.file_path = path
                st.session_state.file_name = uploaded_file.name
                st.session_state.messages = []
                st.session_state.file_type = uploaded_file.name.split(".")[-1].lower()

                if st.session_state.file_type == "csv":
                    df = pd.read_csv(path)
                    df.columns = [c.lower().strip() for c in df.columns]
                    st.session_state.df_columns = list(df.columns)

        if st.session_state.file_name:
            st.divider()
            file_icon = "📄" if st.session_state.file_type == "pdf" else "📊"
            st.success(f"{file_icon} {st.session_state.file_name}")

            if st.session_state.file_type == "csv" and st.session_state.df_columns:
                with st.expander("📄 Dataset Preview"):
                    df_preview = pd.read_csv(st.session_state.file_path).head()
                    df_preview.columns = [c.lower().strip() for c in df_preview.columns]
                    st.dataframe(df_preview, use_container_width=True)

                with st.expander("📌 Available Columns"):
                    for col in st.session_state.df_columns:
                        st.code(col)

        st.divider()

        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chroma_rebuilt = False
            st.rerun()

        st.caption("Runs 100% locally. No data leaves your machine.")


def display_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("chart"):
                st.write(msg["content"])
                st.image(msg["chart"])
            elif msg.get("sources"):
                st.write(msg["content"])
                with st.expander("📎 Source Chunks"):
                    for i, src in enumerate(msg["sources"]):
                        st.caption(f"[{i + 1}] {src[:250]}...")
            else:
                st.write(msg["content"])


def handle_result(result, question):
    msg = {"role": "assistant", "content": "", "chart": None, "sources": None}

    if "error" in result:
        msg["content"] = f"⚠️ {result['error']}"

    elif result["type"] == "pdf":
        msg["content"] = result["answer"]
        msg["sources"] = result.get("sources", [])

    elif result["type"] == "csv":
        msg["content"] = str(result["answer"])
        msg["chart"] = result.get("chart")

    return msg


def main():
    init_session()
    sidebar()

    st.markdown("## 💬 Ask Anything")

    if not st.session_state.file_path:
        st.info("👈 Upload a PDF or CSV from the sidebar to get started.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **📄 PDF Support**
            - Upload any PDF document
            - Ask questions in plain English
            - Get answers with source references
            """)
        with col2:
            st.markdown("""
            **📊 CSV Support**
            - Upload any CSV dataset
            - Ask analytical questions
            - Get charts and insights
            """)
        return

    display_chat()

    question = st.chat_input("Ask a question about your file...")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question, "chart": None, "sources": None}
        )

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = route(st.session_state.file_path, question, OUTPUT_DIR)

            msg = handle_result(result, question)

            if msg["chart"]:
                st.write(msg["content"])
                st.image(msg["chart"])
            elif msg["sources"]:
                st.write(msg["content"])
                with st.expander("📎 Source Chunks"):
                    for i, src in enumerate(msg["sources"]):
                        st.caption(f"[{i + 1}] {src[:250]}...")
            else:
                st.write(msg["content"])

        st.session_state.messages.append(msg)
        st.rerun()


if __name__ == "__main__":
    main()
