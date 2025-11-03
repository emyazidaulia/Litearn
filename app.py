# ===========================================
# 📚 AI Perangkum PDF – Versi Aman & Stabil
# ===========================================

import streamlit as st
import os

# Coba impor pustaka PDF modern (pypdf) lalu fallback ke PyPDF2 jika perlu
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        st.error("❌ Library PDF belum terinstal. Tambahkan 'pypdf' atau 'PyPDF2' ke requirements.txt.")
        st.stop()

from openai import OpenAI

# ==========================
# 🔑 PENGATURAN API KEY
# ==========================
# Jangan menulis API key langsung di kode.
# Gunakan Streamlit Secrets atau .env untuk keamanan.
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY belum diset. Tambahkan API key di Streamlit Cloud → Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ==========================
# 🧠 Fungsi: Ekstrak teks dari PDF
# ==========================
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Gagal membaca PDF: {e}")
        return ""

# ==========================
# ✂️ Fungsi: Bagi teks jadi potongan kecil
# ==========================
def split_text(text, chunk_size=2000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# ==========================
# 🧾 Fungsi: Ringkas teks dengan GPT
# ==========================
def summarize_text(text_chunk):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cepat & hemat, bisa ganti gpt-4-turbo
            messages=[
                {"role": "system", "content": "Kamu adalah asisten yang ahli dalam meringkas dokumen panjang."},
                {"role": "user", "content": f"Ringkas teks berikut menjadi poin-poin utama dengan bahasa mudah:\n\n{text_chunk}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Terjadi kesalahan saat meringkas: {e}"

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

    if not text:
        st.warning("Tidak ada teks yang berhasil dibaca dari PDF. Pastikan PDF bukan hasil scan gambar.")
        st.stop()

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

        st.download_button(
            label="💾 Unduh Ringkasan sebagai TXT",
            data=final_summary,
            file_name="ringkasan_ai.txt",
            mime="text/plain"
        )

        st.success("🎉 Ringkasan selesai dibuat!")
else:
    st.info("Silakan unggah file PDF terlebih dahulu.")
