import streamlit as st

st.title("AI Document Reviewer")
st.write("Upload document → Get review report (no auto-fix)")

uploaded_file = st.file_uploader(
    "Upload Word / PDF / TXT",
    type=["txt", "pdf", "docx"]
)

def read_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    if file.type == "application/pdf":
        from pypdf import PdfReader
        reader = PdfReader(file)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n[Page {i+1}]\n"
            text += page.extract_text()
        return text

    if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

from docx import Document

def extract_text_from_word(uploaded_file):
    doc = Document(uploaded_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

        
text = "This is a simple test document with typo and English word like machine learning."
if uploaded_file:
    text = extract_text_from_word(uploaded_file)
    st.subheader("DEBUG: Extracted Text Preview")
    st.text_area("", text[:3000], height=200)
    st.write("Total characters:", len(text))

chunks = split_text(text)
st.write("Total chunks:", len(chunks))
st.write("First chunk length:", len(chunks[0]))

from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def split_text(text, max_chars=2000):
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) < max_chars:
            current += line + "\n"
        else:
            chunks.append(current)
            current = line + "\n"
    if current:
        chunks.append(current)
    return chunks

REVIEW_PROMPT = """
You are a professional document reviewer.

IMPORTANT RULES:
- Do NOT edit or rewrite the document
- Do NOT correct anything directly
- ONLY provide a review report

Create a structured REVIEW REPORT with sections:
1. Typographical issues
2. Grammar issues
3. English words or phrases that should be italicized
4. Formatting or structural inconsistencies
5. Bullet or numbering problems
6. Improvement suggestions (optional)

For each issue:
- Describe the issue clearly
- Mention page number or section if detectable
- Be concise and professional
"""

import time
from openai import RateLimitError

def ai_review(text):
    chunks = split_text(text)
    reports = []

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            reports.append(f"=== CHUNK {i+1} EMPTY ===")
            continue

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": REVIEW_PROMPT},
                {"role": "user", "content": chunk}
            ]
        )

        content = response.choices[0].message.content

        if not content:
            reports.append(f"=== CHUNK {i+1} RETURNED EMPTY ===")
        else:
            reports.append(f"=== CHUNK {i+1} ===\n{content}")

    return "\n\n".join(reports)


if uploaded_file:
    if st.button("Generate Review Report"):
        with st.spinner("AI is reviewing the document..."):
            report = ai_review(text)
            st.subheader("AI Review Report")
            st.text_area("", report, height=500)
