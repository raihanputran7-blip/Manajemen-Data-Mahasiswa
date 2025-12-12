import streamlit as st
import pandas as pd
import os
import re

# -----------------------
# Konfigurasi warna & file
# -----------------------
DATA_FILE = "data_mahasiswa.csv"
CREDENTIALS = {"dilah": "april"}  # demo credentials

# Warna tema (soft pink)
PAGE_BG = "#FFF6FA"       # very light pink background
CARD_BG = "#FFEAF2"       # card background
PRIMARY = "#FF6FA3"       # main button color (soft hot-pink)
ACCENT = "#FF85B9"        # accent
LOGOUT_BG = "#FF7F50"     # logout (coral-ish)
TEXT_PRIMARY = "#333333"

# -----------------------
# CSS Styling (soft, aesthetic)
# -----------------------
st.set_page_config(page_title="Manajemen Data Mahasiswa", layout="wide")
st.markdown(
    f"""
    <style>
    /* page */
    .stApp {{
        background: linear-gradient(180deg, {PAGE_BG}, #FFFFFF);
    }}
    /* card containers */
    .card {{
        background: {CARD_BG};
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }}
    /* headings */
    .header-title {{
        font-family: 'Helvetica', Arial, sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        margin: 0;
        padding: 0;
    }}
    .header-sub {{
        color: #6b6b6b;
        margin-top: 4px;
        margin-bottom: 0;
        font-size: 14px;
    }}
    /* global buttons */
    .stButton>button, .stDownloadButton>button {{
        background-color: {PRIMARY};
        color: #fff;
        border-radius: 10px;
        padding: 8px 14px;
        border: none;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}
    .stButton>button:hover {{
        opacity: 0.95;
    }}
    /* logout button override (target by containing div) */
    .logout-col .stButton>button {{
        background-color: {LOGOUT_BG} !important;
    }}
    /* inputs */
    input[type="text"], input[type="number"], .stTextArea textarea {{
        border-radius: 8px;
        padding: 8px;
    }}
    /* smaller muted text */
    .muted {{
        color: #6b6b6b;
        font-size: 0.95rem;
    }}
    /* table tweaks */
    .stDataFrame table {{
        border-radius: 8px;
        overflow: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Safe rerun helper
# -----------------------
def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        st.session_state['_refresh_flag'] = not st.session_state.get('_refresh_flag', False)
        st.stop()

# -----------------------
# Utility: baca / simpan
# -----------------------
def ensure_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["NIM", "NAMA", "JENIS KELAMIN", "JURUSAN", "SEMESTER", "IPK"])
        df.to_csv(DATA_FILE, index=False)

def read_data():
    ensure_file()
    return pd.read_csv(DATA_FILE, dtype=str).fillna("")

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)

# -----------------------
# Auth Helpers
# -----------------------
def login(username, password):
    return username in CREDENTIALS and CREDENTIALS[username] == password

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

# -----------------------
# Validation
# -----------------------
def valid_nim(nim):
    return bool(re.fullmatch(r'\d{12}', nim))

def valid_ipk(ipk_str):
    try:
        v = float(ipk_str)
        return 0.0 <= v <= 4.0
    except:
        return False

# -----------------------
# Session init
# -----------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
if '_refresh_flag' not in st.session_state:
    st.session_state['_refresh_flag'] = False

# -----------------------
# Login screen
# -----------------------
if not st.session_state['logged_in']:
    # minimal centered card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="header-title">Masuk ke Aplikasi</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-sub">Silakan login untuk mengakses manajemen data mahasiswa</p>', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login(username.strip(), password.strip()):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username.strip()
                st.success(f"Login berhasil. Selamat datang, {username.strip()}!")
                safe_rerun()
            else:
                st.error("Username atau password salah.")
    st.markdown('<p class="muted">Demo credentials: <strong>dilah</strong> / <strong>april</strong></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Header with logout at far right
    header_col, logout_col = st.columns([0.85, 0.15])
    with header_col:
        st.markdown('<p class="header-title">Manajemen Data Mahasiswa</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="header-sub">Login sebagai: <strong>{st.session_state.get("username")}</strong></p>', unsafe_allow_html=True)
    with logout_col:
        # We add wrapper div so logout button gets styled differently via CSS selector
        st.markdown('<div class="logout-col">', unsafe_allow_html=True)
        if st.button("Logout"):
            logout()
            safe_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Load data
    df = read_data()

    # Two-column layout: left form (card), right table (card)
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Tambah Data")
        with st.form("tambah"):
            nim = st.text_input("NIM (12 digit)", placeholder="Contoh: 200300400500")
            nama = st.text_input("Nama", placeholder="Contoh: Siti Aminah")
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            jurusan = st.text_input("Jurusan", placeholder="Contoh: Teknik Informatika")
            semester = st.number_input("Semester", min_value=1, max_value=14, value=1, step=1)
            ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, value=0.0, step=0.01, format="%.2f")
            simpan = st.form_submit_button("Simpan")
            if simpan:
                nim_str = str(nim).strip()
                if not (nim_str and nama.strip() and jurusan.strip()):
                    st.error("Semua field harus diisi.")
                elif not valid_nim(nim_str):
                    st.error("NIM harus 12 digit angka.")
                elif (df["NIM"].astype(str) == nim_str).any():
                    st.error("NIM sudah ada.")
                elif not valid_ipk(str(ipk)):
                    st.error("IPK harus antara 0.0 dan 4.0.")
                else:
                    new_row = {
                        "NIM": nim_str,
                        "NAMA": nama.strip(),
                        "JENIS KELAMIN": jk,
                        "JURUSAN": jurusan.strip(),
                        "SEMESTER": str(int(semester)),
                        "IPK": f"{float(ipk):.2f}"
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success("Data berhasil ditambahkan.")
                    safe_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Edit / Hapus (card)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Edit Data")
        nim_list = df["NIM"].astype(str).tolist()
        if nim_list:
            nim_pilih = st.selectbox("Pilih NIM untuk edit", [""] + nim_list)
            if nim_pilih:
                row = df[df["NIM"].astype(str) == nim_pilih].iloc[0]
                with st.form("edit_form"):
                    e_nama = st.text_input("Nama", value=row["NAMA"])
                    e_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=0 if row["JENIS KELAMIN"]=="Laki-laki" else 1)
                    e_jur = st.text_input("Jurusan", value=row["JURUSAN"])
                    e_sem = st.number_input("Semester", min_value=1, max_value=14, value=int(row["SEMESTER"]) if row["SEMESTER"]!="" else 1, step=1)
                    e_ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, value=float(row["IPK"]) if row["IPK"]!="" else 0.0, step=0.01, format="%.2f")
                    do_update = st.form_submit_button("Simpan Perubahan")
                    if do_update:
                        if not (e_nama.strip() and e_jur.strip()):
                            st.error("Nama dan Jurusan harus diisi.")
                        elif not valid_ipk(str(e_ipk)):
                            st.error("IPK harus antara 0.0 dan 4.0.")
                        else:
                            df.loc[df["NIM"].astype(str) == nim_pilih, ["NAMA","JENIS KELAMIN","JURUSAN","SEMESTER","IPK"]] = [
                                e_nama.strip(), e_jk, e_jur.strip(), str(int(e_sem)), f"{float(e_ipk):.2f}"
                            ]
                            save_data(df)
                            st.success("Data berhasil diperbarui.")
                            safe_rerun()
                # Hapus sebagai button terpisah (bukan form) sehingga tidak perlu klik 2x
                if st.button("Hapus Data", key=f"del_{nim_pilih}"):
                    df = df[df["NIM"].astype(str) != nim_pilih].reset_index(drop=True)
                    save_data(df)
                    st.success("Data berhasil dihapus.")
                    safe_rerun()
        else:
            st.info("Belum ada data untuk diedit atau dihapus.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Data Mahasiswa")
        st.markdown('<p class="muted">Filter, urutkan, dan unduh data CSV.</p>', unsafe_allow_html=True)

        # Filter & sorting controls
        keyword = st.text_input("Cari (NIM atau Nama)", "")
        sort_opt = st.selectbox("Urutkan berdasarkan", ["NIM", "NAMA", "IPK"])
        dir_opt = st.selectbox("Arah urutan", ["Ascending", "Descending"])

        df_display = df.copy()
        if keyword:
            kw = keyword.strip().lower()
            df_display = df_display[
                df_display["NIM"].astype(str).str.contains(kw, case=False) |
                df_display["NAMA"].astype(str).str.lower().str.contains(kw)
            ]

        if not df_display.empty:
            if sort_opt == "IPK":
                df_display["IPK_sort"] = pd.to_numeric(df_display["IPK"], errors="coerce").fillna(0.0)
                df_display = df_display.sort_values(by="IPK_sort", ascending=(dir_opt=="Ascending")).drop(columns=["IPK_sort"])
            else:
                df_display = df_display.sort_values(by=sort_opt, ascending=(dir_opt=="Ascending"))

        st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

        # Download CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_bytes, file_name="data_mahasiswa.csv", mime="text/csv")

        st.markdown('</div>', unsafe_allow_html=True)

    # footer note
    st.markdown("<br/>")
    st.info("Catatan: File CSV tersimpan pada filesystem instance. Pada deploy gratis data bisa hilang saat instance direstart. Untuk persistensi, gunakan database (SQLite/Supabase).")
