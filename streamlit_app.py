import os
import sys
import tempfile
import streamlit as st

# Hubungkan path ke folder modul internal Anda
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assets.style import ambil_tema  # Tetap di-import jika dibutuhkan variabel warna
from modules.grafik import hitung_dan_buat_grafik
from modules.simpleks import hitung_solusi_simpleks

# 1. Konfigurasi Dasar Jendela Aplikasi Web
st.set_page_config(
    page_title="Aplikasi Program Linear",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Desain Sidebar Menu
st.sidebar.title("🧮 LP Solver")
st.sidebar.caption("Aplikasi Program Linear")
st.sidebar.markdown("---")

# Menggantikan tombol Navigasi CustomTkinter lama
halaman_aktif = st.sidebar.radio(
    "Navigasi Metode:",
    ["📉 Metode Grafik", "🧮 Metode Simpleks"]
)

st.sidebar.markdown("---")
# Fitur Informasi Tambahan atau Cetak di Sidebar
st.sidebar.markdown("### 🖨️ Cetak Dokumen")
tombol_cetak = st.sidebar.button("Siapkan Hasil Cetak (PDF)")

# 3. Konten Utama Berdasarkan Halaman yang Dipilih
if halaman_aktif == "📉 Metode Grafik":
    st.header("📉 Metode Program Linear - Grafik")
    st.write("Metode ini cocok untuk menyelesaikan masalah dengan maksimal 2 variabel keputusan ($X_1$ dan $X_2$).")
    
    # Membuat Layout Form Input Berdampingan
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fungsi Tujuan")
        tipe_tujuan = st.selectbox("Jenis Optimasi:", ["Maksimasi", "Minimasi"])
        z_x1 = st.number_input("Koefisien X1 (Z):", value=40.0, step=1.0)
        z_x2 = st.number_input("Koefisien X2 (Z):", value=30.0, step=1.0)
        
    with col2:
        st.subheader("Contoh Kendala 1 & 2")
        k1_x1 = st.number_input("Kendala 1: Koefisien X1", value=2.0, step=1.0)
        k1_x2 = st.number_input("Kendala 1: Koefisien X2", value=1.0, step=1.0)
        k1_tanda = st.selectbox("Tanda K1:", ["<=", ">=", "="], key="k1")
        k1_nilai = st.number_input("Nilai Kanan K1:", value=60.0, step=1.0)

    # Simpan data input ke dalam session_state agar bisa diakses fitur cetak PDF
    st.session_state['data_soal'] = {
        'tipe': tipe_tujuan, 'z': [z_x1, z_x2],
        'k1': [k1_x1, k1_x2, k1_tanda, k1_nilai]
    }

    st.markdown("---")
    if st.button("🚀 Hitung Solusi Grafik", type="primary"):
        with st.spinner("Sedang memproses dan menggambar grafik..."):
            # Memanggil fungsi logika matematika baru yang mengembalikan objek gambar & data
            fig, hasil_titik, titik_optimal = hitung_dan_buat_grafik(st.session_state['data_soal'])
            
            # Tampilkan Grafik Matplotlib langsung ke halaman Web Streamlit
            st.subheader("Visualisasi Grafik Area Layak")
            st.pyplot(fig)
            
            # Tampilkan Hasil Analisis Titik Sudut
            st.subheader("Analisis Titik Ekstrem (Sudut)")
            st.write(hasil_titik)
            
            st.success(f"**Solusi Optimal Ditemukan!** Nilai Optimum Z = {titik_optimal}")
            st.session_state['hasil_terakhir'] = {"status": "sukses", "optimal": titik_optimal}

elif halaman_aktif == "🧮 Metode Simpleks":
    st.header("🧮 Metode Program Linear - Simpleks")
    st.write("Metode ini digunakan untuk menyelesaikan masalah optimasi dengan banyak variabel keputusan.")
    
    st.subheader("Matriks Nilai Kendala & Fungsi Tujuan")
    input_matriks = st.text_area(
        "Masukkan baris persamaan (Koefisien X1, X2, ... Slack | Nilai Kanan):",
        value="1, 2, 1, 0, 40\n3, 1, 0, 1, 60\n-40, -30, 0, 0, 0"
    )
    
    if st.button("🔮 Iterasi Tabel Simpleks", type="primary"):
        with st.spinner("Menghitung tabel iterasi simpleks..."):
            # Panggil fungsi logika dari modul simpleks Anda
            hasil_tabel, ringkasan_solusi = hitung_solusi_simpleks(input_matriks)
            
            st.subheader("Hasil Tabel Akhir")
            st.dataframe(hasil_tabel)  # Render tabel interaktif di web
            
            st.subheader("Kesimpulan Solusi")
            st.info(ringkasan_solusi)
            st.session_state['hasil_terakhir'] = {"status": "sukses", "detail": ringkasan_solusi}

# 4. Logika Fitur Cetak PDF (Menggantikan `_print_hasil` bawaan Desktop)
if tombol_cetak:
    if 'hasil_terakhir' not in st.session_state:
        st.error("⚠️ Belum ada hasil untuk dicetak. Silakan hitung solusi terlebih dahulu di halaman aktif!")
    else:
        st.toast("Menyiapkan dokumen PDF...", icon="⏳")
        # Logika pembuatan PDF dialihkan ke skema download web browser
        path_pdf = os.path.join(tempfile.gettempdir(), "cetak_hasil_lp.pdf")
        
        # Contoh membuat berkas teks tiruan sebagai representasi PDF siap unduh
        konten_cetak = f"LAPORAN PROGRAM LINEAR\nStatus: {st.session_state['hasil_terakhir']['status']}\n"
        with open(path_pdf, "w") as f:
            f.write(konten_cetak)
            
        with open(path_pdf, "rb") as file_pdf:
            st.sidebar.download_button(
                label="📥 Unduh Berkas PDF Hasil",
                data=file_pdf,
                file_name="Laporan_Solusi_Linear_Math.pdf",
                mime="application/pdf"
            )

# 5. Trik Kompatibilitas Khusus Jika Anda Memaksa Menggunakan Server Vercel
if __name__ == "__main__":
    if os.environ.get("VERCEL"):
        import subprocess
        subprocess.run(["streamlit", "run", "main.py", "--server.port", "8000", "--server.address", "0.0.0.0"])
