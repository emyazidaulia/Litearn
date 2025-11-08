import os
import streamlit as st
import PyPDF2
import requests

# ============================================================
# KONFIGURASI API KEY (ambil dari Streamlit Secrets)
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

# ============================================================
# KONFIGURASI MODEL UTAMA & CADANGAN
# ============================================================
PRIMARY_MODEL = "llama-3.1-8b-instant"  # model aktif Groq
FALLBACK_MODEL = "mixtral-8x7b"         # fallback jika model utama gagal

# ============================================================
# FUNGSI UNTUK MEMBACA PDF
# ============================================================
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# ============================================================
# FUNGSI UNTUK MERINGKAS DENGAN GROQ API
# ============================================================
def summarize_with_groq(text, model=PRIMARY_MODEL):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Kamu adalah asisten AI yang pandai meringkas teks dalam bahasa Indonesia secara singkat dan padat."},
                {"role": "user", "content": f"Ringkas isi teks berikut secara jelas dan terstruktur:\n\n{text}"}
            ],
            "temperature": 0.4,
            "max_tokens": 1024
        }

        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()

        # fallback otomatis jika model utama gagal
        elif response.status_code == 400 and "decommissioned" in response.text.lower():
            st.warning("⚠️ Model utama sudah tidak tersedia. Menggunakan model cadangan...")
            return summarize_with_groq(text, model=FALLBACK_MODEL)
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"Gagal meringkas dengan Groq API: {e}")
        return None

# ============================================================
# ANTARMUKA STREAMLIT
# ============================================================
st.set_page_config(page_title="AI Peringkas PDF", page_icon="🧠", layout="centered")
st.title("🧠 AI Peringkas PDF Otomatis")
st.write("Unggah file PDF dan dapatkan ringkasan cepat menggunakan model AI Groq.")

uploaded_file = st.file_uploader("📄 Unggah file PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("🔍 Membaca file PDF..."):
        text = extract_text_from_pdf(uploaded_file)
        if len(text) < 100:
            st.error("PDF terlalu singkat atau tidak memiliki teks yang bisa dibaca.")
        else:
            st.success("✅ Teks berhasil diekstrak dari PDF.")
            st.subheader("📘 Cuplikan Teks:")
            st.write(text[:1000] + ("..." if len(text) > 1000 else ""))

            if st.button("🚀 Ringkas Sekarang"):
                with st.spinner("🤖 AI sedang membuat ringkasan..."):
                    summary = summarize_with_groq(text)
                    if summary:
                        st.success("✨ Ringkasan Berhasil Dibuat!")
                        st.subheader("📝 Hasil Ringkasan:")
                        st.write(summary)
                        st.download_button("💾 Unduh Ringkasan", summary, file_name="ringkasan.pdf")

else:
    st.info("Silakan unggah file PDF terlebih dahulu untuk memulai.")

# ============================================================
# CATATAN
# ============================================================
st.markdown("""
---
💡 **Tips:**
- Pastikan Anda sudah menambahkan API Key Groq di **Streamlit → Settings → Secrets**  
  Dalam format TOML berikut:
