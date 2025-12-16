import streamlit as st
import time
from docx import Document
from pypdf import PdfReader
from openai import OpenAI

# =========================
# CONFIG & CLIENT
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI Document Reviewer")
st.write("Upload document → Get review report (no auto-fix)")

uploaded_file = st.file_uploader(
    "Upload Word / PDF / TXT",
    type=["txt", "pdf", "docx"]
)

# =========================
# TEXT EXTRACTORS
# =========================
def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += f"\n[Page {i+1}]\n{page_text}"
    return text

def extract_text_from_word(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_text(file):
    if file.type == "text/plain":
        return extract_text_from_txt(file)

    if file.type == "application/pdf":
        return extract_text_from_pdf(file)

    if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_word(file)

    return ""

# =========================
# TEXT SPLITTER
# =========================
def split_text(text, max_chars=4000):
    chunks = []
    current = ""

    for line in text.split("\n"):
        if len(current) + len(line) <= max_chars:
            current += line + "\n"
        else:
            chunks.append(current)
            current = line + "\n"

    if current.strip():
        chunks.append(current)

    return chunks

# =========================
# PROMPT
# =========================
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

# =========================
# AI REVIEW FUNCTION
# =========================
from openai import RateLimitError

def ai_review(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": text[:8000]}  # LIMIT
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# =========================
# UI FLOW
# =========================
if uploaded_file:
    text = read_text(uploaded_file)

    st.subheader("DEBUG: Extracted Text Preview")
    st.text_area("", text[:3000], height=200)
    st.write("Total characters:", len(text))

    chunks = split_text(text)
    st.write("Total chunks:", len(chunks))
    st.write("First chunk length:", len(chunks[0]) if chunks else 0)

    if st.button("Generate Review Report"):
        with st.spinner("AI is reviewing the document..."):
            report = ai_review(text)

        st.subheader("AI Review Report")
        st.text_area("", report, height=500)
