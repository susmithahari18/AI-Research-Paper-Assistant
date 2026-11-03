
import streamlit as st
import hashlib

from modules.pdf_loader import extract_text_from_pdf
from modules.text_splitter import split_text_into_chunks

from modules.embeddings import (
    create_vector_store,
    retrieve_relevant_chunks
)

from modules.rag_pipeline import generate_answer


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Research AI Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "vector_store": None,
    "uploaded_file_name": None,
    "uploaded_file_hash": None,
    "chat_history": [],
    "total_pages": 0,
    "total_chunks": 0,
    "pdf_name": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main-header {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 5px;
}

.sub-header {
    color: #888888;
    font-size: 15px;
    margin-bottom: 25px;
}

.answer-card {
    padding: 22px;
    border-radius: 12px;
}

div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📚 Research AI")

    st.caption("Your Intelligent Research Companion")

    st.divider()

    st.subheader("Navigation")

    st.markdown("🏠 **Home**")
    st.markdown("📄 Document Analysis")
    st.markdown("💬 Chat History")

    st.divider()

    st.subheader("Document Information")

    if st.session_state.pdf_name:

        st.write("**Uploaded File**")
        st.caption(st.session_state.pdf_name)

        st.metric(
            "Total Pages",
            st.session_state.total_pages
        )

        st.metric(
            "Total Text Chunks",
            st.session_state.total_chunks
        )

        st.success("Document Ready")

    else:

        st.info("Upload a PDF to get started.")

    st.divider()

    st.subheader("Project Information")

    st.write("**Project:** Research AI Assistant")
    st.write("**Language:** Python")
    st.write("**Framework:** Streamlit")
    st.write("**AI Model:** Gemini 3.5 Flash")
    st.write("**Vector Database:** FAISS")

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):

        st.session_state.chat_history = []
        st.rerun()


# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    '<div class="main-header">AI Research Paper Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-header">'
    'Upload your research paper, analyze its content, '
    'and get intelligent answers using AI.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# PDF UPLOAD
# ==========================================

st.subheader("📄 Upload Research Paper")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload your research paper in PDF format."
)


if uploaded_file is not None:

    try:

        # ----------------------------------
        # SHA-256 FILE HASHING
        # ----------------------------------

        file_bytes = uploaded_file.getvalue()

        file_hash = hashlib.sha256(
            file_bytes
        ).hexdigest()

        # ----------------------------------
        # DETECT NEW PDF
        # ----------------------------------

        if st.session_state.uploaded_file_hash != file_hash:

            st.session_state.vector_store = None
            st.session_state.chat_history = []

            st.session_state.total_pages = 0
            st.session_state.total_chunks = 0

            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_file_hash = file_hash
            st.session_state.pdf_name = uploaded_file.name

        # ----------------------------------
        # PDF PROCESSING
        # ----------------------------------

        if st.session_state.vector_store is None:

            with st.spinner("Extracting PDF text..."):

                uploaded_file.seek(0)

                pages = extract_text_from_pdf(uploaded_file)

            if not pages:

                st.error("No extractable text found in this PDF.")
                st.stop()

            st.success("PDF extracted successfully!")

            # ----------------------------------
            # TEXT CHUNKING
            # ----------------------------------

            chunks = split_text_into_chunks(pages)

            if not chunks:

                st.error("No text chunks generated.")
                st.stop()

            # ----------------------------------
            # CREATE EMBEDDINGS AND FAISS
            # ----------------------------------

            with st.spinner(
                "Generating embeddings and creating FAISS database..."
            ):

                vector_store = create_vector_store(chunks)

            st.session_state.vector_store = vector_store

            st.session_state.total_pages = len(pages)
            st.session_state.total_chunks = len(chunks)

            st.success("Embeddings generated successfully!")
            st.success("FAISS Vector Database created!")

        else:

            st.success(
                f"Research paper ready: {uploaded_file.name}"
            )

        # ==================================
        # DOCUMENT STATISTICS
        # ==================================

        st.divider()

        st.subheader("📊 Document Overview")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Pages",
                st.session_state.total_pages
            )

        with col2:

            st.metric(
                "Text Chunks",
                st.session_state.total_chunks
            )

        with col3:

            st.metric(
                "AI Model",
                "Gemini 3.5 Flash"
            )

        # ==================================
        # EXTRACTED TEXT VIEW
        # ==================================

        with st.expander("View Extracted PDF Text"):

            uploaded_file.seek(0)

            pages = extract_text_from_pdf(uploaded_file)

            for page in pages:

                st.markdown(
                    f"**Page {page['page']}**"
                )

                st.write(page["text"])

                st.divider()

        # ==================================
        # QUESTION INPUT
        # ==================================

        st.divider()

        st.subheader("💬 Ask Your Research Question")

        with st.form("question_form", clear_on_submit=True):

            question = st.text_input(
                "Enter your question",
                placeholder="Example: What is the main objective of this research?"
            )

            search_button = st.form_submit_button(
                "🔍 Search Document",
                type="primary",
                use_container_width=True
            )

        # ==================================
        # QUESTION PROCESSING
        # ==================================

        if search_button:

            if question.strip():

                with st.spinner("Searching relevant information..."):

                    results = retrieve_relevant_chunks(
                        st.session_state.vector_store,
                        question
                    )

                if not results:

                    st.warning("No relevant information found.")

                else:

                    with st.spinner("Generating AI answer..."):

                        answer = generate_answer(
                            question,
                            results
                        )

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer
                    })

                    st.success("Answer generated successfully!")

            else:

                st.warning("Please enter your question.")

        # ==================================
        # LATEST AI ANSWER
        # ==================================

        if st.session_state.chat_history:

            latest_chat = st.session_state.chat_history[-1]

            st.divider()

            st.subheader("🤖 AI Generated Answer")

            with st.container(border=True):

                st.markdown(latest_chat["answer"])

        # ==================================
        # CHAT HISTORY
        # ==================================

        st.divider()

        st.subheader("🕘 Previous Conversations")

        if st.session_state.chat_history:

            for index, chat in enumerate(
                reversed(st.session_state.chat_history)
            ):

                question_number = (
                    len(st.session_state.chat_history) - index
                )

                with st.expander(
                    f"Question {question_number}: {chat['question']}"
                ):

                    st.markdown("**AI Generated Answer**")

                    st.markdown(chat["answer"])

        else:

            st.info(
                "No conversations yet. Ask your first question above."
            )

    except Exception as error:

        st.error(f"An error occurred: {error}")

else:

    st.info("Please upload a research paper PDF to get started.")

    st.markdown("""
    ### What you can do with Research AI

    - Upload research papers in PDF format.
    - Extract and process research content.
    - Search relevant information using semantic search.
    - Generate structured AI answers.
    - View previous conversations.
    """)
