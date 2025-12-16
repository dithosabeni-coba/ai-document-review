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
  
