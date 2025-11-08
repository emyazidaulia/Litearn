import os
import streamlit as st
import PyPDF2
import requests

# ============================================================
# KONFIGURASI API KEY (ambil dari Streamlit Secrets)
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# ============================================================
# KONFIGURASI MODEL UTAMA & CADANGAN
# ============================================================
PRIMARY_MODEL = "llama-3.1-8b-instant"  # ganti sesuai model yang tersedia di akun Groq Anda
FALLBACK_MODEL = "mixtral-8x7b"         # model cadangan jika model utama tidak tersedia

# ============================================================
# FUNGSI UNTUK MEMBACA PDF
# ============================================================
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        st.error(f"Gagal mengekstrak teks dari PDF: {e}")
        return ""

# ============================================================
# FUNGSI UNTUK MERINGKAS DENGAN GROQ API (dengan fallback model)
# ============================================================
def summarize_with_groq(text, model=PRIMARY_MODEL):
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY tidak ditemukan. Tambahkan GROQ_API_KEY di Streamlit Secrets.")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten AI yang pandai meringkas teks dalam bahasa Indonesia secara singkat dan padat."},
            {"role": "user", "content": f"Ringkas isi teks berikut secara jelas dan terstruktur:\n\n{text}"}
        ],
        "temperature": 0.4,
        "max_tokens": 1024
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as re:
        st.error(f"Gagal memanggil Groq API (network error): {re}")
        return None

    # Berhasil
    if resp.status_code == 200:
        try:
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            st.error(f"Gagal membaca respon dari Groq API: {e}")
            return None

    # Model decommissioned — coba fallback model
    if resp.status_code == 400 and "decommissioned" in resp.text.lower():
        st.warning("⚠️ Model utama tidak tersedia/didekomision. Menggunakan model cadangan...")
        # Jika fallback sama dengan primary, hentikan untuk mencegah loop
        if model == FALLBACK_MODEL:
            st.error("Model cadangan juga dipilih sebagai model utama, tidak ada model lain untuk dicoba.")
            return None
        return summarize_with_groq(text, model=FALLBACK_MODEL)

    # Jika error terkait API key atau kuota, tampilkan pesan jelas
    if resp.status_code == 401:
        st.error("401 Unauthorized — API key tidak valid atau telah dicabut. Periksa GROQ_API_KEY di Streamlit Secrets.")
        return None
    if resp.status_code == 429:
        st.error("429 Too Many Requests / Quota exceeded — kuota Groq Anda mungkin habis.")
        return None

    # Untuk error lain, tampilkan pesan singkat dan log body
    st.error(f"Groq API mengembalikan error {resp.status_code}.")
    st.text(resp.text)
    return None

# ============================================================
# ANTARMUKA STREAMLIT
# ============================================================
st.set_page_config(page_title="AI Peringkas PDF", page_icon="🧠", layout="centered")
st.title("🧠 AI Peringkas PDF Otomatis")
st.write("Unggah file PDF dan dapatkan ringkasan cepat menggunakan model AI Groq.")

# Upload file
uploaded_file = st.file_uploader("📄 Unggah file PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("🔍 Membaca file PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if not text:
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
                    st.download_button("💾 Unduh Ringkasan", summary, file_name="ringkasan.txt", mime="text/plain")
                else:
                    st.warning("⚠️ Tidak berhasil meringkas teks. Periksa API key atau log.")
else:
    st.info("Silakan unggah file PDF terlebih dahulu untuk memulai.")
