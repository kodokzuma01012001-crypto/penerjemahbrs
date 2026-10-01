import streamlit as st
import pdfplumber
import pandas as pd
import json

# Setup halaman Streamlit
st.set_page_config(
    page_title="Penerjemah BRS BPS Kepri",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Penerjemah Berita Resmi Statistik (BRS)")
st.caption("BPS Provinsi Kepulauan Riau - Otomasi Terjemahan BRS Bahasa Indonesia ke Bahasa Inggris")

# ---------------------------------------------------------
# 1. MANAGEMENT GLOSARIUM ISTILAH STATISTIK
# ---------------------------------------------------------
DEFAULT_GLOSSARY = {
    "Inflasi year-on-year": "Year-on-year inflation",
    "Inflasi month-to-month": "Month-to-month inflation",
    "Tingkat Pengangguran Terbuka (TPT)": "Open Unemployment Rate (OUR)",
    "Produk Domestik Regional Bruto (PDRB)": "Gross Regional Domestic Product (GRDP)",
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": "Labor Force Participation Rate (LFPR)",
    "Garis Kemiskinan": "Poverty Line",
    "Persentase Penduduk Miskin": "Percentage of Poor Population",
    "Nilai Tukar Petani (NTP)": "Farmers' Term of Trade (FTT)",
    "Jumlah Wisatawan Mancanegara": "Number of Foreign Tourist Visits",
    "Tingkat Penghunian Kamar (TPK)": "Room Occupancy Rate (ROR)",
    "Indeks Pembangunan Manusia (IPM)": "Human Development Index (HDI)"
}

st.sidebar.header("⚙️ Pengaturan & Glosarium")
st.sidebar.write("Glosarium ini memastikan konsistensi istilah statistik BPS.")

# Tampilkan dan izinkan pengguna mengedit glosarium
glossary_df = pd.DataFrame(
    list(DEFAULT_GLOSSARY.items()), 
    columns=["Bahasa Indonesia (Asli)", "Bahasa Inggris (Standar)"]
)

edited_glossary = st.sidebar.data_editor(
    glossary_df, 
    num_rows="dynamic", 
    use_container_width=True,
    key="glossary_editor"
)

# Konversi glosarium terevaluasi kembali ke dictionary
active_glossary = dict(zip(
    edited_glossary["Bahasa Indonesia (Asli)"], 
    edited_glossary["Bahasa Inggris (Standar)"]
))


# ---------------------------------------------------------
# 2. FUNGSI EKSTRAKSI PDF
# ---------------------------------------------------------
def extract_text_from_pdf(pdf_file):
    extracted_pages = []
    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append({"page": i + 1, "text": text})
    return extracted_pages


# ---------------------------------------------------------
# 3. INTERFACE UTAMA - UPLOAD FILE
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Upload File BRS (.pdf)", type=["pdf"])

if uploaded_file is not None:
    st.success(f"File **{uploaded_file.name}** berhasil diunggah!")
    
    with st.spinner("Mengekstrak teks dari PDF..."):
        pages_data = extract_text_from_pdf(uploaded_file)
    
    st.info(f"Total Halaman Terdeteksi: {len(pages_data)}")
    
    # Gabungkan teks untuk opsi terjemahkan seluruh dokumen
    full_text_id = "\n\n".join([f"--- Halaman {p['page']} ---\n{p['text']}" for p in pages_data])
    
    # Tab Tampilan
    tab1, tab2 = st.tabs(["📄 Teks Terekstrak", "🚀 Terjemahkan"])
    
    with tab1:
        st.subheader("Hasil Ekstraksi Teks PDF")
        st.text_area("Teks Asli (Bahasa Indonesia):", value=full_text_id, height=400)
        
    with tab2:
        st.subheader("Proses Penerjemahan dengan Glosarium")
        st.write("Sistem akan menerapkan pemetaan istilah statistik berikut saat menerjemahkan:")
        
        # Display preview glosarium yang aktif
        st.json(active_glossary, expanded=False)
        
        if st.button("Mulai Terjemahkan ke Bahasa Inggris", type="primary"):
            with st.spinner("Menerjemahkan teks dan menyelaraskan istilah statistik..."):
                # Di sini tempat integrasi API LLM (misal: Gemini API)
                # Contoh prompt yang diproduksi untuk API:
                prompt_instruction = f"""
                Anda adalah penerjemah profesional Berita Resmi Statistik (BRS) Badan Pusat Statistik (BPS).
                Tugas Anda adalah menerjemahkan teks BRS berikut dari Bahasa Indonesia ke Bahasa Inggris baku.
                
                ATURAN WAJIB:
                1. Gunakan glosarium istilah statistik berikut tanpa mengecualikan satu pun:
                   {json.dumps(active_glossary, ensure_ascii=False, indent=2)}
                2. Pertahankan keakuratan angka, angka desimal, simbol persentase, dan tanggal.
                3. Pertahankan struktur paragraf dan header/sub-header.
                
                Teks Asli:
                {full_text_id}
                """
                
                # Simulasi/Dummy Output untuk Pratinjau Tampilan Dashboard
                # (Di produksi, ganti bagian ini dengan panggilan model LLM)
                translated_text_en = f"--- Page 1 ---\nOfficial Statistics News (BRS) Translation Result for {uploaded_file.name}\n\n"
                translated_text_en += "[Hasil terjemahan otomatis bahasa Inggris dari AI akan muncul di sini secara lengkap sesuai struktur paragraf dan aturan glosarium]."
                
                st.session_state['translated_result'] = translated_text_en
                st.success("Penerjemahan Selesai!")

        # Tampilkan Hasil Terjemahan jika sudah selesai
        if 'translated_result' in st.session_state:
            st.divider()
            col_id, col_en = st.columns(2)
            
            with col_id:
                st.markdown("### 🇮🇩 Teks Asli (Indonesia)")
                st.text_area("Teks Indonesia", value=full_text_id, height=450, key="preview_id")
                
            with col_en:
                st.markdown("### 🇬🇧 Hasil Terjemahan (Inggris)")
                st.text_area("Teks Inggris", value=st.session_state['translated_result'], height=450, key="preview_en")
                
            st.download_button(
                label="📥 Unduh Hasil Terjemahan (.txt)",
                data=st.session_state['translated_result'],
                file_name=f"BRS_English_{uploaded_file.name.replace('.pdf', '.txt')}",
                mime="text/plain"
            )