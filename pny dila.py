import streamlit as st
import pandas as pd
import os
import re

DATA_FILE = "data_mahasiswa.csv"
CREDENTIALS = {"dilah": "april"}  # demo credentials

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

def valid_semester(sem):
    try:
        v = int(sem)
        return 1 <= v <= 14
    except:
        return False

# -----------------------
# Session init
# -----------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

st.set_page_config(page_title="Manajemen Data Mahasiswa", layout="wide")

# -----------------------
# Login screen
# -----------------------
if not st.session_state['logged_in']:
    st.title("Masuk ke Aplikasi")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login(username.strip(), password.strip()):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username.strip()
                st.success(f"Login berhasil. Selamat datang, {username.strip()}!")
                st.experimental_rerun()
            else:
                st.error("Username atau password salah.")
    st.info("Coba username: dilah dan password: april (demo).")
else:
    # Header dan logout
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("Manajemen Data Mahasiswa")
        st.write(f"Login sebagai: {st.session_state.get('username')}")
    with col2:
        if st.button("Logout"):
            logout()
            st.experimental_rerun()

    # Load data
    df = read_data()

    # Layout: kiri (form), kanan (tabel)
    left, right = st.columns([1, 2])

    with left:
        st.subheader("Tambah Data")
        with st.form("tambah"):
            nim = st.text_input("NIM (12 digit)")
            nama = st.text_input("Nama")
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            jurusan = st.text_input("Jurusan")
            semester = st.number_input("Semester", min_value=1, max_value=14, value=1, step=1)
            ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, step=0.01, value=0.0, format="%.2f")
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
                    st.experimental_rerun()

        st.markdown("---")
        st.subheader("Edit / Hapus Data")
        nim_list = df["NIM"].astype(str).tolist()
        if nim_list:
            nim_pilih = st.selectbox("Pilih NIM untuk edit/hapus", [""] + nim_list)
            if nim_pilih:
                row = df[df["NIM"].astype(str) == nim_pilih].iloc[0]
                with st.form("edit_form"):
                    e_nama = st.text_input("Nama", value=row["NAMA"])
                    e_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=0 if row["JENIS KELAMIN"]=="Laki-laki" else 1)
                    e_jur = st.text_input("Jurusan", value=row["JURUSAN"])
                    e_sem = st.number_input("Semester", min_value=1, max_value=14, value=int(row["SEMESTER"]) if row["SEMESTER"]!="" else 1, step=1)
                    e_ipk = st.number_input("IPK", min_value=0.0, max_value=4.0, value=float(row["IPK"]) if row["IPK"]!="" else 0.0, step=0.01, format="%.2f")
                    do_update = st.form_submit_button("Simpan Perubahan")
                    do_delete = st.form_submit_button("Hapus Data")
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
                            st.experimental_rerun()
                    if do_delete:
                        df = df[df["NIM"].astype(str) != nim_pilih].reset_index(drop=True)
                        save_data(df)
                        st.success("Data berhasil dihapus.")
                        st.experimental_rerun()
        else:
            st.info("Belum ada data untuk diedit atau dihapus.")

    with right:
        st.subheader("Data Mahasiswa")
        # Filter & sorting controls
        keyword = st.text_input("Cari (NIM atau Nama)", "")
        sort_opt = st.selectbox("Urutkan berdasarkan", ["NIM", "NAMA", "IPK"])
        dir_opt = st.selectbox("Arah urutan", ["Ascending", "Descending"])

        df_display = df.copy()
        if keyword:
            kw = keyword.strip().lower()
            df_display = df_display[df_display["NIM"].astype(str).str.contains(kw, case=False) | df_display["NAMA"].astype(str).str.lower().str.contains(kw)]

        if not df_display.empty:
            if sort_opt == "IPK":
                df_display["IPK_sort"] = pd.to_numeric(df_display["IPK"], errors="coerce").fillna(0.0)
                df_display = df_display.sort_values(by="IPK_sort", ascending=(dir_opt=="Ascending")).drop(columns=["IPK_sort"])
            else:
                df_display = df_display.sort_values(by=sort_opt, ascending=(dir_opt=="Ascending"))

        st.dataframe(df_display.reset_index(drop=True))

        # Download CSV
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_bytes, file_name="data_mahasiswa.csv", mime="text/csv")

        st.markdown("---")
        st.info("Catatan: Pada deploy gratis, file CSV tersimpan di filesystem instance yang ephemeral — pertimbangkan database untuk persistensi jangka panjang.")
