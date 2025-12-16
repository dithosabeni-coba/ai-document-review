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
        doc = Document(file)
        text = ""
        for i, para in enumerate(doc.paragraphs):
            text += para.text + "\n"
        return text

if uploaded_file:
    text = read_text(uploaded_file)
    st.subheader("Extracted Text (Preview)")
    st.text_area("", text[:3000], height=300)
  
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

def ai_review(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": REVIEW_PROMPT
            },
            {
                "role": "user",
                "content": text[:12000]
            }
        ]
    )
    return response.choices[0].message.content

if uploaded_file:
    if st.button("Generate Review Report"):
        with st.spinner("AI is reviewing the document..."):
            report = ai_review(text)
            st.subheader("AI Review Report")
            st.text_area("", report, height=500)
