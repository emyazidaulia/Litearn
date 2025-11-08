import streamlit as st
import os
import subprocess
import sys

# ==============================================================
# ✅ BAGIAN 1: Instalasi otomatis paket yang belum ada
# ==============================================================

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        st.error(f"Gagal menginstal paket {package}: {e}")

try:
    import PyPDF2
except ModuleNotFoundError:
    st.warning("📦 Menginstal PyPDF2...")
    install_package("PyPDF2")
    import PyPDF2

try:
    from groq import Groq
except ModuleNotFoundError:
    st.warning("📦 Menginstal groq SDK...")
    install_package("groq")
    from groq import Groq


# ==============================================================
# ✅ BAGIAN 2: Konfigurasi halaman Streamlit
# ==============================================================

st.set_page_config(page_title="📄 AI PDF Summarizer (Groq)", layout="wide")
st.title("📘 AI PDF Summarizer - Groq Model")
st.write("Unggah file PDF dan dapatkan ringkasannya secara otomatis menggunakan AI dari **Groq** 🚀")

# ==============================================================
# ✅ BAGIAN 3: Ambil API Key dari Streamlit Secrets
# ==============================================================

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ API Key tidak ditemukan. Pastikan kamu sudah menambahkan `GROQ_API_KEY` di Secrets.")
    st.stop()

# ==============================================================
# ✅ BAGIAN 4: Upload dan ekstraksi teks PDF
# ==============================================================

uploaded_file = st.file_uploader("📂 Unggah file PDF", type=["pdf"])

def extract_text_from_pdf(file):
    """Ekstrak teks dari file PDF."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Gagal membaca PDF: {e}")
        return ""

text = ""
if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if text.strip():
        st.success("✅ Berhasil mengekstrak teks dari PDF!")
        with st.expander("📖 Lihat isi PDF"):
            st.text_area("Isi Teks PDF:", text, height=300)
    else:
        st.warning("⚠️ Tidak ditemukan teks dalam PDF ini.")

# ==============================================================
# ✅ BAGIAN 5: Fungsi Peringkasan dengan Groq
# ==============================================================

def summarize_with_groq(text, api_key):
    """Meringkas teks menggunakan API Groq."""
    try:
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",  # model cepat dari Groq
            messages=[
                {"role": "system", "content": "Kamu adalah asisten AI yang ahli dalam meringkas dokumen panjang."},
                {"role": "user", "content": f"Ringkas teks berikut dalam bahasa Indonesia:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        st.error(f"❌ Gagal meringkas dengan Groq API: {e}")
        return None

# ==============================================================
# ✅ BAGIAN 6: Tombol Ringkas
# ==============================================================

if st.button("🧠 Ringkas PDF"):
    if not uploaded_file:
        st.warning("⚠️ Harap unggah file PDF terlebih dahulu.")
    elif not text.strip():
        st.warning("⚠️ Tidak ada teks yang bisa diringkas.")
    else:
        with st.spinner("⏳ AI Groq sedang meringkas isi PDF..."):
            summary = summarize_with_groq(text, api_key)
        if summary:
            st.subheader("📋 Hasil Ringkasan:")
            st.write(summary)
        else:
            st.warning("⚠️ Tidak berhasil meringkas teks.")

# ==============================================================
# ✅ BAGIAN 7: Footer
# ==============================================================

st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Streamlit + Groq API | 2025")
