# ===========================================
# 📚 AI Perangkum PDF – Versi dengan Fallback Model
# ===========================================

import streamlit as st
import PyPDF2
from openai import OpenAI
import os

# ==========================
# 🔑 Konfigurasi API Key
# ==========================
# ⚠️ Jangan taruh API key langsung di sini untuk keamanan.
# Gunakan menu "Secrets" di Streamlit Cloud atau file .env lokal.
# Contoh: st.secrets["OPENAI_API_KEY"]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    st.error("❌ API Key belum diatur. Tambahkan OPENAI_API_KEY di secrets atau environment variable.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================
# 🧠 Fungsi: Ekstrak teks dari PDF
# ==========================
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Gagal membaca PDF: {e}")
        return ""

# ==========================
# ✂️ Fungsi: Bagi teks jadi potongan kecil
# ==========================
def split_text(text, chunk_size=2000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# ==========================
# 🧾 Fungsi: Ringkas teks dengan fallback model
# ==========================
def summarize_text(text_chunk):
    system_prompt = "Kamu adalah asisten AI yang ahli dalam meringkas teks panjang menjadi poin-poin penting dan mudah dipahami."

    try:
        # Model utama (lebih kuat)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Ringkas teks berikut menjadi poin-poin utama:\n\n{text_chunk}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e)

        # 🧩 Tangani kuota habis
        if "insufficient_quota" in err or "You exceeded your current quota" in err:
            st.warning("⚠️ Kuota API model utama (GPT-4o-mini) habis. Beralih ke model cadangan (GPT-3.5-turbo)...")
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Ringkas teks berikut menjadi poin-poin utama:\n\n{text_chunk}"}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as inner_e:
                return f"⚠️ Gagal juga dengan model cadangan: {inner_e}"

        # 🧩 Tangani API key salah
        elif "invalid_api_key" in err or "Incorrect API key" in err:
            return "❌ API Key salah atau tidak aktif. Periksa pengaturan di https://platform.openai.com/account/api-keys"

        # 🧩 Tangani error lainnya
        else:
            return f"⚠️ Terjadi kesalahan saat meringkas: {err}"

# ==========================
# 🖥️ Tampilan Streamlit
# ==========================
st.set_page_config(page_title="AI Perangkum PDF", page_icon="📘", layout="wide")
st.title("📚 AI Perangkum Buku / PDF")
st.write("Unggah file PDF kamu, dan biarkan AI meringkas isinya secara otomatis ✨")

uploaded_file = st.file_uploader("Unggah file PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("📖 Membaca isi PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if not text.strip():
        st.error("❌ Tidak dapat mengekstrak teks dari file PDF.")
        st.stop()

    st.success(f"✅ PDF berhasil dibaca. Panjang teks: {len(text)} karakter.")

    if len(text) < 500:
        st.warning("⚠️ Teks terlalu pendek untuk diringkas.")
    else:
        chunks = split_text(text)
        st.info(f"🔍 PDF dibagi menjadi {len(chunks)} bagian agar bisa diproses dengan aman.")

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
            label="💾 Unduh Ringkasan (TXT)",
            data=final_summary,
            file_name="ringkasan_ai.txt",
            mime="text/plain"
        )

        st.success("🎉 Ringkasan selesai dibuat!")
else:
    st.info("Silakan unggah file PDF terlebih dahulu.")
