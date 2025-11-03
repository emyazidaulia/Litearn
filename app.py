import streamlit as st
import sys
import subprocess

# ==============================================================
# ✅ BAGIAN 1: Fungsi bantu untuk instalasi otomatis
# ==============================================================

def install_package(package):
    """Instal paket Python secara otomatis jika belum tersedia."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        st.error(f"Gagal menginstal paket {package}: {e}")

# ==============================================================
# ✅ BAGIAN 2: Pastikan dependensi utama tersedia
# ==============================================================

# Pastikan PyPDF2 ada
try:
    import PyPDF2
except ModuleNotFoundError:
    st.warning("📦 Modul PyPDF2 belum terinstal. Menginstal otomatis...")
    install_package("PyPDF2")
    import PyPDF2

# Pastikan scikit-learn ada
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ModuleNotFoundError:
    st.warning("📦 Modul scikit-learn belum terinstal. Menginstal otomatis...")
    install_package("scikit-learn")
    from sklearn.feature_extraction.text import TfidfVectorizer

# Pastikan transformers ada (untuk analisis teks opsional)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ModuleNotFoundError:
    st.warning("📦 Modul transformers belum terinstal. Menginstal otomatis...")
    install_package("transformers")
    try:
        from transformers import pipeline
        TRANSFORMERS_AVAILABLE = True
    except Exception:
        st.warning("❌ Modul transformers gagal dimuat. Akan menggunakan model fallback sederhana.")
        TRANSFORMERS_AVAILABLE = False

# ==============================================================
# ✅ BAGIAN 3: Konfigurasi Streamlit
# ==============================================================

st.set_page_config(page_title="Litearn - PDF Text Analyzer", layout="wide")
st.title("📘 Litearn - PDF Text Analyzer")
st.write("Unggah file PDF Anda untuk diekstrak dan dianalisis teksnya secara otomatis.")

# ==============================================================
# ✅ BAGIAN 4: Upload PDF dan ekstraksi teks
# ==============================================================

uploaded_file = st.file_uploader("📂 Unggah file PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        if text.strip():
            st.success("✅ Berhasil mengekstrak teks dari PDF!")
            st.text_area("📄 Isi PDF:", text, height=300)
        else:
            st.warning("⚠️ Tidak ada teks yang dapat diekstrak dari PDF ini.")
    except Exception as e:
        st.error(f"Gagal membaca file PDF: {e}")
else:
    st.info("Silakan unggah file PDF terlebih dahulu.")

# ==============================================================
# ✅ BAGIAN 5: Analisis teks (opsional)
# ==============================================================

st.subheader("🔍 Analisis Teks (Opsional)")

if st.button("Analisis Sentimen"):
    if uploaded_file is None:
        st.warning("⚠️ Harap unggah PDF terlebih dahulu.")
    elif len(text.strip()) < 10:
        st.warning("⚠️ Tidak cukup teks untuk dianalisis.")
    else:
        try:
            if TRANSFORMERS_AVAILABLE:
                st.info("🔄 Menggunakan model Hugging Face untuk analisis sentimen...")
                classifier = pipeline("sentiment-analysis")
                result = classifier(text[:512])[0]
                st.success(f"**Label:** {result['label']} | **Skor:** {result['score']:.2f}")
            else:
                st.info("🧠 Menggunakan model fallback sederhana (rule-based).")
                positive_words = ["good", "great", "happy", "excellent", "positive", "love"]
                negative_words = ["bad", "sad", "terrible", "poor", "hate", "negative"]

                pos_count = sum(word in text.lower() for word in positive_words)
                neg_count = sum(word in text.lower() for word in negative_words)

                if pos_count > neg_count:
                    st.success(f"Label: POSITIVE | Rasio: {pos_count}:{neg_count}")
                elif neg_count > pos_count:
                    st.error(f"Label: NEGATIVE | Rasio: {pos_count}:{neg_count}")
                else:
                    st.warning("Label: NEUTRAL | Tidak dominan positif atau negatif.")
        except Exception as e:
            st.error(f"❌ Gagal melakukan analisis teks: {e}")

# ==============================================================
# ✅ BAGIAN 6: Footer
# ==============================================================

st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Streamlit | © 2025 Litearn")
