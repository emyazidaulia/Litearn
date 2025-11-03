import streamlit as st
import sys
import subprocess
import os

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
    from openai import OpenAI
except ModuleNotFoundError:
    st.warning("📦 Menginstal openai...")
    install_package("openai")
    from openai import OpenAI

# ==============================================================
# ✅ BAGIAN 2: Konfigurasi halaman Streamlit
# ==============================================================

st.set_page_config(page_title="📄 PDF Summarizer AI", layout="wide")
st.title("📘 AI PDF Summarizer")
st.write("Unggah file PDF dan dapatkan ringkasannya secara otomatis menggunakan AI. 🚀")

# ==============================================================
# ✅ BAGIAN 3: Input API key
# ==============================================================

st.sidebar.header("⚙️ Pengaturan")
api_key = st.sidebar.text_input("Masukkan OpenAI API Key:", type="password")

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
        with st.expander("Lihat isi teks PDF"):
            st.text_area("📄 Isi PDF:", text, height=300)
    else:
        st.warning("⚠️ Tidak ditemukan teks dalam PDF ini.")

# ==============================================================
# ✅ BAGIAN 5: Fungsi peringkasan dengan fallback
# ==============================================================

def summarize_text(text, api_key=None):
    """Meringkas teks menggunakan OpenAI API, atau fallback jika gagal."""
    if not text.strip():
        return "Tidak ada teks yang bisa diringkas."

    # Jika tidak ada API key, langsung pakai fallback
    if not api_key:
        return simple_summarizer(text)

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten AI yang mahir meringkas dokumen."},
                {"role": "user", "content": f"Ringkas teks berikut dalam bahasa Indonesia:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        st.warning(f"⚠️ Terjadi kesalahan pada API ({e}). Menggunakan model fallback lokal.")
        return simple_summarizer(text)

def simple_summarizer(text):
    """Fallback sederhana untuk meringkas teks tanpa AI."""
    sentences = text.split(".")
    if len(sentences) > 5:
        summary = ". ".join(sentences[:5]) + "."
    else:
        summary = text
    return f"(Fallback) Ringkasan sederhana:\n\n{summary.strip()}"

# ==============================================================
# ✅ BAGIAN 6: Tombol Ringkas
# ==============================================================

if st.button("🧠 Ringkas PDF"):
    if not uploaded_file:
        st.warning("⚠️ Harap unggah file PDF terlebih dahulu.")
    elif not text.strip():
        st.warning("⚠️ Tidak ada teks yang bisa diringkas.")
    else:
        with st.spinner("⏳ AI sedang meringkas isi PDF..."):
            summary = summarize_text(text, api_key)
        st.subheader("📋 Hasil Ringkasan:")
        st.write(summary)

# ==============================================================
# ✅ BAGIAN 7: Footer
# ==============================================================

st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Streamlit + OpenAI API | 2025")
