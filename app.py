import os
import streamlit as st
import PyPDF2
import requests
import textwrap

# ============================================================
# KONFIGURASI API KEY (ambil dari Streamlit Secrets)
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# ============================================================
# KONFIGURASI MODEL
# ============================================================
PRIMARY_MODEL = "llama-3.1-8b-instant"
FALLBACK_MODEL = "mixtral-8x7b"

# ============================================================
# FUNGSI: Ekstraksi teks PDF
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
# FUNGSI: Panggil API Groq untuk meringkas
# ============================================================
def call_groq_api(prompt, model=PRIMARY_MODEL):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten AI yang mahir meringkas teks panjang menjadi poin-poin utama dalam bahasa Indonesia."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    elif response.status_code == 400 and "decommissioned" in response.text.lower():
        # fallback jika model utama tidak tersedia
        st.warning("⚠️ Model utama tidak tersedia, menggunakan model cadangan...")
        return call_groq_api(prompt, model=FALLBACK_MODEL)
    else:
        st.error(f"Groq API mengembalikan error {response.status_code}.\n\n{response.text}")
        return None

# ============================================================
# FUNGSI: Ringkas PDF panjang (dibagi jadi beberapa bagian)
# ============================================================
def summarize_large_text(full_text, chunk_size=4000):
    chunks = textwrap.wrap(full_text, width=chunk_size)
    st.info(f"📄 Dokumen besar, dibagi menjadi {len(chunks)} bagian untuk diringkas...")

    partial_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        with st.spinner(f"🧠 Meringkas bagian {i}/{len(chunks)}..."):
            summary = call_groq_api(f"Ringkas teks berikut dengan singkat dan padat:\n\n{chunk}")
            if summary:
                partial_summaries.append(summary)
            else:
                st.warning(f"⚠️ Gagal meringkas bagian {i}")

    combined_text = "\n\n".join(partial_summaries)
    st.success("✅ Semua bagian berhasil diringkas. Sekarang membuat ringkasan akhir...")

    # Ringkas hasil gabungan
    final_summary = call_groq_api(f"Gabungkan dan ringkas keseluruhan hasil berikut menjadi satu ringkasan utuh:\n\n{combined_text}")
    return final_summary

# ============================================================
# ANTARMUKA STREAMLIT
# ============================================================
st.set_page_config(page_title="AI Peringkas PDF", page_icon="🧠", layout="centered")
st.title("🧠 AI Peringkas PDF Otomatis")
st.write("Unggah file PDF dan dapatkan ringkasan cepat menggunakan AI Groq.")

uploaded_file = st.file_uploader("📄 Unggah file PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("📖 Membaca file PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if text:
        st.success("✅ Berhasil mengekstrak teks!")
        st.text_area("📘 Cuplikan teks:", text[:1000] + ("..." if len(text) > 1000 else ""), height=200)

        if st.button("🚀 Ringkas Sekarang"):
            with st.spinner("🤖 AI sedang meringkas..."):
                summary = summarize_large_text(text)
                if summary:
                    st.subheader("📝 Hasil Ringkasan:")
                    st.write(summary)
                    st.download_button("💾 Unduh Ringkasan", summary, file_name="ringkasan.txt", mime="text/plain")
                else:
                    st.warning("⚠️ Tidak berhasil meringkas teks.")
    else:
        st.error("PDF tidak berisi teks yang dapat dibaca.")
else:
    st.info("Silakan unggah file PDF terlebih dahulu.")

