# ===========================================
# 📚 AI Perangkum PDF – Versi Menengah
# Dibuat sederhana agar mudah dipahami
# ===========================================

import streamlit as st
import PyPDF2
from openai import OpenAI
import os

# ==========================
# 🔑 MASUKKAN API KEY DI SINI
# ==========================
# Disarankan simpan di file .env untuk keamanan
os.environ["OPENAI_API_KEY"] = "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"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================
# 🧠 Fungsi: Ekstrak teks dari PDF
# ==========================
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# ==========================
# ✂️ Fungsi: Bagi teks jadi potongan kecil
# ==========================
def split_text(text, chunk_size=2000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# ==========================
# 🧾 Fungsi: Ringkas teks dengan GPT
# ==========================
def summarize_text(text_chunk):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # bisa juga gpt-3.5-turbo jika lebih murah
            messages=[
                {"role": "system", "content": "Kamu adalah asisten yang ahli dalam meringkas dokumen panjang."},
                {"role": "user", "content": f"Ringkas teks berikut menjadi poin-poin utama dengan bahasa mudah:\n\n{text_chunk}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Terjadi kesalahan saat meringkas: {e}"

# ==========================
# 🖥️ Tampilan Streamlit
# ==========================
st.set_page_config(page_title="AI Perangkum PDF", page_icon="📘", layout="wide")
st.title("📚 AI Perangkum PDF/Buku")
st.write("Unggah file PDF kamu, dan biarkan AI meringkas isinya secara otomatis!")

uploaded_file = st.file_uploader("Unggah file PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("📖 Membaca isi PDF..."):
        text = extract_text_from_pdf(uploaded_file)
    
    st.success(f"✅ PDF berhasil dibaca. Panjang teks: {len(text)} karakter.")

    if len(text) < 500:
        st.warning("Teks terlalu pendek untuk diringkas.")
    else:
        chunks = split_text(text)
        st.info(f"🔍 PDF dibagi menjadi {len(chunks)} bagian agar bisa diringkas dengan aman.")

        summaries = []
        progress = st.progress(0)
        for i, chunk in enumerate(chunks):
            summary = summarize_text(chunk)
            summaries.append(summary)
            progress.progress((i + 1) / len(chunks))
        
        final_summary = "\n\n".join(summaries)
        
        st.subheader("📘 Ringkasan Akhir")
        st.write(final_summary)

        # Tombol download ringkasan
        st.download_button(
            label="💾 Unduh Ringkasan sebagai TXT",
            data=final_summary,
            file_name="ringkasan_ai.txt",
            mime="text/plain"
        )

        st.success("🎉 Ringkasan selesai dibuat!")
else:
    st.info("Silakan unggah file PDF terlebih dahulu.")
