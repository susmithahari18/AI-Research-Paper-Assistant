
# AI Research Paper Assistant

An AI-powered application that helps users understand research papers by asking questions and receiving context-based answers.

## Features

- Upload research papers in PDF format
- Extract text from PDF documents
- Split text into chunks
- Generate semantic embeddings
- Store embeddings using FAISS
- Retrieve relevant content using similarity search
- Generate structured answers using Google Gemini
- Maintain conversation history

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- LangChain
- FAISS
- PyPDF

## Project Architecture

PDF Upload → Text Extraction → Text Chunking → Embeddings → FAISS Vector Database → Similarity Search → Gemini LLM → AI Answer

## Installation

1. Clone the repository:

   git clone YOUR_REPOSITORY_URL

2. Navigate to the project:

   cd AI-Research-Paper-Assistant

3. Create a virtual environment:

   python -m venv venv

4. Activate it:

   Windows:
   venv\Scripts\activate

5. Install dependencies:

   pip install -r requirements.txt

6. Create a `.env` file:

   GOOGLE_API_KEY=your_google_api_key

7. Run the application:

   streamlit run app.py

## Author

Susmitha Hari
