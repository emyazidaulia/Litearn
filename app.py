import streamlit as st
import PyPDF2
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

st.title("📚 AI Peringkas Buku")

uploaded_file = st.file_uploader("Upload file PDF buku", type=["pdf"])

if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    if st.button("Ringkas Buku"):
        with st.spinner("Sedang meringkas..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Kamu adalah asisten AI yang pandai meringkas teks buku."},
                    {"role": "user", "content": f"Ringkas isi buku berikut secara singkat:\n\n{text}"}
                ]
            )
            summary = response.choices[0].message.content
            st.subheader("Hasil Ringkasan:")
            st.write(summary)
            st.download_button("Download Ringkasan", summary, "ringkasan.txt")
