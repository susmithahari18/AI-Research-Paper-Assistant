
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_answer(question, retrieved_chunks):

    # Validate API key
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "Google API key not found. Check your .env file."
        )

    # Validate question
    if not question or not question.strip():
        raise ValueError("Please enter a valid question.")

    # Validate retrieved context
    if not retrieved_chunks:
        raise ValueError("No relevant information was retrieved.")

    # Initialize Gemini client
    client = genai.Client(
        api_key=api_key,
        http_options={"timeout": 120000}
    )

    # Prepare context
    context = "\n\n".join(
        [
            f"Page {chunk['page']}: {chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    # Create prompt
    prompt = f"""
You are a professional AI Research Paper Assistant.

Answer using ONLY the provided research paper context.

Follow this exact structure:

## 1. Summary
- Maximum 3 sentences.

## 2. Key Findings
- Maximum 5 bullet points.

## 3. Methodology
- Explain briefly.
- If unavailable, state that it was not found in the uploaded paper.

## 4. Conclusion
- Maximum 3 bullet points.

Rules:
- Start directly with Summary.
- Use professional and clear language.
- Never invent information.
- Do not repeat information.
- Do not include source excerpts.
- Mention page numbers where relevant.

Research Paper Context:
{context}

User Question:
{question}
"""

    # Generate answer
    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    except Exception as error:

        error_message = str(error).lower()

        if "timeout" in error_message:
            raise RuntimeError(
                "Gemini request timed out. Please try again."
            ) from error

        elif "503" in error_message or "unavailable" in error_message:
            raise RuntimeError(
                "Gemini is temporarily unavailable. Please try again later."
            ) from error

        elif "429" in error_message or "quota" in error_message:
            raise RuntimeError(
                "Gemini API quota exceeded. Check your API usage."
            ) from error

        else:
            raise RuntimeError(
                f"Gemini answer generation failed: {error}"
            ) from error
