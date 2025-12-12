import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
import csv
import os
import sys

# ==============================
# KONFIGURASI GLOBAL & STYLE
# ==============================
DATA_FILE = "data_mahasiswa.csv"
BG_SOFT = "#FFD1DC"  # Soft Pink
FG_BUTTON = "#FF69B4" # Hot Pink for contrast
BG_FRAME = "#F0F0F0" # Light Gray for contrast
FONT_BOLD = ("Helvetica", 10, "bold")
SORT_OPTIONS = ["NIM", "Nama", "IPK"]
# JURUSAN_OPTIONS dihapus karena sekarang menggunakan entry manual

# ==============================
# OOP
# ==============================
class Person:
    """Class dasar untuk Orang."""
    def __init__(self, nama=""):
        self._nama = nama

    @property
    def nama(self):
        return self._nama

    @nama.setter
    def nama(self, value):
        self._nama = value

class Mahasiswa(Person):
    """Class turunan untuk Mahasiswa, menerapkan pewarisan dan enkapsulasi."""
    def __init__(self, nim="", nama="", jenis_kelamin="", jurusan="", semester=0, ipk=0.0):
        super().__init__(nama)
        self._nim = nim
        self._jenis_kelamin = jenis_kelamin
        self._jurusan = jurusan
        self._semester = int(semester)
        self._ipk = float(ipk)

    def getNIM(self): return self._nim
    def setNIM(self, nim): self._nim = nim
    def getJenisKelamin(self): return self._jenis_kelamin
    def setJenisKelamin(self, jk): self._jenis_kelamin = jk
    def getJurusan(self): return self._jurusan
    def setJurusan(self, jur): self._jurusan = jur
    def getSemester(self): return self._semester
    def setSemester(self, sem): self._semester = int(sem)
    def getIPK(self): return self._ipk
    def setIPK(self, ipk): self._ipk = float(ipk)
    
    def __repr__(self):
        return f"{self._nim},{self._nama},{self._jenis_kelamin},{self._jurusan},{self._semester},{self._ipk}"

# ==============================
# DATA & FILE I/O
# ==============================
data_mahasiswa = []

def simpan_ke_file():
    """Menyimpan data_mahasiswa ke file CSV (File I/O)."""
    try:
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["NIM", "NAMA", "JENIS KELAMIN", "JURUSAN", "SEMESTER", "IPK"])
            for m in data_mahasiswa:
                writer.writerow([m.getNIM(), m.nama, m.getJenisKelamin(), m.getJurusan(), m.getSemester(), m.getIPK()])
    except IOError as e:
        messagebox.showerror("Error I/O", f"Gagal menyimpan file: {e}")

def baca_dari_file():
    """Membaca data dari file CSV (File I/O, Try-Catch)."""
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) == 6:
                    # Pastikan konversi tipe data saat membaca
                    try:
                        semester_val = int(row[4]) if row[4] else 0
                        ipk_val = float(row[5]) if row[5] else 0.0
                        m = Mahasiswa(row[0], row[1], row[2], row[3], semester_val, ipk_val)
                        data_mahasiswa.append(m)
                    except ValueError:
                        continue
    except Exception as e:
        messagebox.showerror("Error I/O", f"Terjadi error saat membaca file: {e}")

# ==============================
# SEARCH & SORT ALGORITHMS
# ==============================
def linear_search(nim):
    """Pencarian Sekuensial (Linear Search). Time Complexity: O(n)"""
    for i, m in enumerate(data_mahasiswa):
        if m.getNIM() == nim:
            return i
    return -1

def get_sort_key(attr_name):
    """Mendapatkan fungsi key untuk sorting dinamis."""
    if attr_name == "NIM":
        return lambda m: m.getNIM()
    elif attr_name == "Nama":
        return lambda m: m.nama.upper()
    elif attr_name == "IPK":
        return lambda m: m.getIPK()
    return lambda m: m.getNIM()

def bubble_sort(key_func, reverse=False):
    """Bubble Sort. Time Complexity: O(n^2)"""
    n = len(data_mahasiswa)
    for i in range(n):
        for j in range(0, n - i - 1):
            compare = key_func(data_mahasiswa[j]) > key_func(data_mahasiswa[j+1])
            if reverse: compare = not compare
            if compare:
                data_mahasiswa[j], data_mahasiswa[j+1] = data_mahasiswa[j+1], data_mahasiswa[j]
    messagebox.showinfo("Sorting", "Data diurutkan menggunakan Bubble Sort.")

def insertion_sort(key_func, reverse=False):
    """Insertion Sort. Time Complexity: O(n^2)"""
    for i in range(1, len(data_mahasiswa)):
        key_item = data_mahasiswa[i]
        j = i - 1
        while j >= 0:
            compare = key_func(data_mahasiswa[j]) > key_func(key_item)
            if reverse: compare = not compare
            if compare:
                data_mahasiswa[j + 1] = data_mahasiswa[j]
                j -= 1
            else: break
        data_mahasiswa[j + 1] = key_item

def merge_sort(key_func, reverse=False):
    """Merge Sort. Time Complexity: O(n log n)"""
    def merge(left, right, key, rev):
        result = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            compare = key(left[i]) < key(right[j])
            if rev: compare = not compare
            if compare: result.append(left[i]); i += 1
            else: result.append(right[j]); j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def sort_recursive(data_list, key, rev):
        if len(data_list) <= 1: return data_list
        mid = len(data_list) // 2
        left = sort_recursive(data_list[:mid], key, rev)
        right = sort_recursive(data_list[mid:], key, rev)
        return merge(left, right, key, rev)
    
    global data_mahasiswa
    data_mahasiswa = sort_recursive(data_mahasiswa, key_func, reverse)
    # Feedback di messagebox dipindah ke fungsi pemanggil (show_sort_popup)

# ==============================
# LOGIN WINDOW
# ==============================
class LoginWindow:
    """Toplevel login simple. Credentials: dilah / april"""
    def __init__(self, master):
        self.master = master
        self.authenticated = False
        self.top = tk.Toplevel(master)
        self.top.title("Login")
        self.top.geometry("320x180")
        self.top.resizable(False, False)
        self.top.configure(bg=BG_FRAME)
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

        tk.Label(self.top, text="Masuk ke Aplikasi", bg=BG_FRAME, font=FONT_BOLD).pack(pady=10)

        frame = tk.Frame(self.top, bg=BG_FRAME)
        frame.pack(padx=10, pady=5, fill='x')

        tk.Label(frame, text="Username", bg=BG_FRAME).grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var).grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password", bg=BG_FRAME).grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*").grid(row=1, column=1, pady=5)

        btn_frame = tk.Frame(self.top, bg=BG_FRAME)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Login", command=self.attempt_login, bg=FG_BUTTON, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Batal", command=self.on_close).pack(side=tk.LEFT, padx=5)

        # Fokus ke entry username
        self.top.after(100, lambda: self.top.focus_force())

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        # Kredensial statis sesuai permintaan
        if username == "dilah" and password == "april":
            self.authenticated = True
            messagebox.showinfo("Login Berhasil", f"Selamat datang, {username}!")
            self.top.destroy()
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")

    def on_close(self):
        # Tutup login -> hapus top dan biarkan main memutuskan (program akan keluar jika tidak authenticated)
        self.authenticated = False
        self.top.destroy()

# ==============================
# GUI APP UTAMA
# ==============================
class App:
    """Kelas utama aplikasi GUI."""
    def __init__(self, root):
        self.root = root
        self.root.title("Manajemen Data Mahasiswa")
        self.root.geometry("1000x700")  # Increased height for logout button
        self.root.configure(bg=BG_SOFT)

        self.jk_var = tk.StringVar(value="Laki-laki")
        self.sort_criteria_var = tk.StringVar(value=SORT_OPTIONS[0]) 
        self.sort_direction_var = tk.StringVar(value="Ascending")

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        frame_input = tk.Frame(self.root, bg=BG_FRAME, padx=10, pady=10, relief=tk.GROOVE)
        frame_input.pack(pady=10, padx=10, fill='x')

        # ROW 0: NIM dan Jenis Kelamin
        tk.Label(frame_input, text="NIM", bg=BG_FRAME, font=FONT_BOLD).grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nim = ttk.Entry(frame_input, width=25)
        self.entry_nim.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(frame_input, text="Jenis Kelamin", bg=BG_FRAME, font=FONT_BOLD).grid(row=0, column=2, sticky="w", padx=10, pady=2)
        jk_frame = tk.Frame(frame_input, bg=BG_FRAME)
        jk_frame.grid(row=0, column=3, sticky="w", pady=2)
        tk.Radiobutton(jk_frame, text="Laki-laki", variable=self.jk_var, value="Laki-laki", bg=BG_SOFT, selectcolor=FG_BUTTON, indicatoron=0, width=10).pack(side="left", padx=3)
        tk.Radiobutton(jk_frame, text="Perempuan", variable=self.jk_var, value="Perempuan", bg=BG_SOFT, selectcolor=FG_BUTTON, indicatoron=0, width=10).pack(side="left", padx=3)

        # ROW 1: Nama
        tk.Label(frame_input, text="Nama", bg=BG_FRAME, font=FONT_BOLD).grid(row=1, column=0, sticky="w", pady=2)
        self.entry_nama = ttk.Entry(frame_input, width=40)
        self.entry_nama.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        # ROW 2: Jurusan dan Semester (Jurusan sekarang Entry manual)
        tk.Label(frame_input, text="Jurusan", bg=BG_FRAME, font=FONT_BOLD).grid(row=2, column=0, sticky="w", pady=2)
        self.entry_jurusan = ttk.Entry(frame_input, width=25) # Menggunakan Entry
        self.entry_jurusan.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        tk.Label(frame_input, text="Semester", bg=BG_FRAME, font=FONT_BOLD).grid(row=2, column=2, sticky="w", padx=10, pady=2)
        # Menggunakan Spinbox untuk semester
        self.spinbox_semester = tk.Spinbox(frame_input, from_=1, to_=14, width=5)
        self.spinbox_semester.grid(row=2, column=3, padx=5, pady=2, sticky="w")

        # ROW 3: IPK dan Tombol Aksi
        tk.Label(frame_input, text="IPK (0.0-4.0)", bg=BG_FRAME, font=FONT_BOLD).grid(row=3, column=0, sticky="w", pady=2)
        self.entry_ipk = ttk.Entry(frame_input, width=10)
        self.entry_ipk.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.entry_ipk.insert(0, "0.0")

        # Tombol Simpan
        btn_simpan = tk.Button(frame_input, text="Simpan Data", command=self.simpan_data, bg=FG_BUTTON, fg="white", font=FONT_BOLD)
        btn_simpan.grid(row=3, column=2, columnspan=2, pady=10, sticky="e")

        # --- Frame untuk Sorting dan Aksi Tabel ---
        frame_controls = tk.Frame(self.root, bg=BG_SOFT, padx=10, pady=5)
        frame_controls.pack(pady=5, padx=10, fill='x')

        # Sorting Controls
        tk.Label(frame_controls, text="Urutkan berdasarkan:", bg=BG_SOFT).pack(side=tk.LEFT, padx=5)
        ttk.Combobox(frame_controls, textvariable=self.sort_criteria_var, values=SORT_OPTIONS, state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Combobox(frame_controls, textvariable=self.sort_direction_var, values=["Ascending", "Descending"], state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_controls, text="Urutkan Data", command=self.show_sort_popup, bg=FG_BUTTON, fg="white").pack(side=tk.LEFT, padx=10) # Memanggil popup sort

        # Action Buttons
        tk.Button(frame_controls, text="Edit Data", command=self.show_edit_popup, bg=FG_BUTTON, fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(frame_controls, text="Hapus Data", bg="red", fg="white", command=self.hapus_data).pack(side=tk.RIGHT, padx=5)

        # Tombol Logout di pojok kanan paling atas kontrol
        tk.Button(frame_controls, text="Logout", command=self.logout, bg="#FF7F50", fg="white").pack(side=tk.RIGHT, padx=10)

        # --- Tabel Data (Treeview) ---
        frame_table = tk.Frame(self.root, bg=BG_FRAME, padx=10, pady=10)
        frame_table.pack(pady=10, padx=10, fill='both', expand=True)

        columns = ("NIM", "Nama", "Jenis Kelamin", "Jurusan", "Semester", "IPK")
        self.tree = ttk.Treeview(frame_table, columns=columns, show='headings')
        
        # Konfigurasi heading dan lebar kolom
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER, width=100)
        
        self.tree.column("Nama", width=200)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill='both', expand=True)

    def validate_input(self, nim, nama, jurusan, semester, ipk_str):
        """Validasi input sebelum disimpan."""
        if not all([nim, nama, jurusan, ipk_str]):
            messagebox.showerror("Input Error", "Semua field harus diisi.")
            return False
        if not re.fullmatch(r'\d{12}', nim):
            messagebox.showerror("Input Error", "NIM harus 12 digit angka.")
            return False
        try:
            ipk = float(ipk_str)
            if not (0.0 <= ipk <= 4.0):
                messagebox.showerror("Input Error", "IPK harus antara 0.0 sampai 4.0.")
                return False
            semester_val = int(semester)
            if not (1 <= semester_val <= 14):
                 messagebox.showerror("Input Error", "Semester harus antara 1 sampai 14.")
                 return False
        except ValueError:
            messagebox.showerror("Input Error", "IPK dan Semester harus berupa angka yang valid.")
            return False
        return True

    def simpan_data(self):
        """Menambahkan data mahasiswa baru."""
        nim = self.entry_nim.get()
        nama = self.entry_nama.get()
        jenis_kelamin = self.jk_var.get()
        jurusan = self.entry_jurusan.get() # Ambil dari Entry
        semester = self.spinbox_semester.get()
        ipk_str = self.entry_ipk.get()

        if not self.validate_input(nim, nama, jurusan, semester, ipk_str):
            return

        if linear_search(nim) != -1:
            messagebox.showerror("Duplikasi Data", f"Mahasiswa dengan NIM {nim} sudah ada.")
            return

        m = Mahasiswa(nim, nama, jenis_kelamin, jurusan, semester, ipk_str)
        data_mahasiswa.append(m)
        simpan_ke_file()
        self.refresh_table()
        self.clear_entries()
        messagebox.showinfo("Sukses", "Data berhasil ditambahkan.")

    def clear_entries(self):
        """Membersihkan field input."""
        self.entry_nim.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.entry_jurusan.delete(0, tk.END)
        # jangan reset ipk/semester agar pengguna bisa cepat input beberapa data serupa

    def refresh_table(self):
        """Memperbarui tampilan Treeview."""
        # Hapus semua item yang ada
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Masukkan data terbaru
        for m in data_mahasiswa:
            self.tree.insert('', tk.END, values=(m.getNIM(), m.nama, m.getJenisKelamin(), m.getJurusan(), m.getSemester(), m.getIPK()))

    def hapus_data(self):
        """Menghapus data mahasiswa yang dipilih."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus terlebih dahulu.")
            return

        # Ambil NIM dari item yang dipilih di treeview
        item_values = self.tree.item(selected_item, 'values')
        nim_to_delete = item_values[0] # Ambil NIM (elemen pertama)

        # Cari index di list data_mahasiswa
        index = linear_search(nim_to_delete)
        if index != -1:
            del data_mahasiswa[index]
            simpan_ke_file()
            self.refresh_table()
            messagebox.showinfo("Sukses", "Data berhasil dihapus.")
        else:
            messagebox.showerror("Error", "Data tidak ditemukan dalam database.")

    def apply_sort(self, sort_algorithm_func, window):
        """Menerapkan sorting yang dipilih dari pop up."""
        criteria = self.sort_criteria_var.get()
        direction = self.sort_direction_var.get()
        reverse = (direction == "Descending")
        key_func = get_sort_key(criteria)
        
        sort_algorithm_func(key_func, reverse)
        
        self.refresh_table()
        window.destroy() # Tutup pop-up
        messagebox.showinfo("Sorting Selesai", f"Data diurutkan menggunakan {sort_algorithm_func.__name__} berdasarkan {criteria} secara {direction}.")


    def show_sort_popup(self):
        """Menampilkan pop-up window untuk memilih algoritma sorting."""
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Pilih Algoritma Sorting")
        sort_window.geometry("250x150")
        sort_window.configure(bg=BG_FRAME)

        tk.Label(sort_window, text="Pilih Algoritma Pengurutan:", bg=BG_FRAME, font=FONT_BOLD).pack(pady=10)

        # Tombol untuk memilih algoritma
        btn_merge = tk.Button(sort_window, text="Merge Sort (O(n log n))", command=lambda: self.apply_sort(merge_sort, sort_window), bg=FG_BUTTON, fg="white", width=25)
        btn_merge.pack(pady=5)

        btn_bubble = tk.Button(sort_window, text="Bubble Sort (O(n^2))", command=lambda: self.apply_sort(bubble_sort, sort_window), bg=FG_BUTTON, fg="white", width=25)
        btn_bubble.pack(pady=5)
        
        # Fokuskan pop up dan tunggu sampai ditutup
        sort_window.grab_set()
        self.root.wait_window(sort_window)

    # ====================================================================
    # FITUR EDIT DATA DENGAN Pop-up Window
    # ====================================================================
    def show_edit_popup(self):
        """Menampilkan pop-up window untuk mengedit data yang dipilih."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin diedit terlebih dahulu.")
            return

        # Ambil data dari baris yang dipilih
        item_values = self.tree.item(selected_item, 'values')
        nim_to_edit = item_values[0] # Ambil NIM (elemen pertama)
        
        # Cari objek Mahasiswa yang sesuai di list global
        index = linear_search(nim_to_edit)
        if index == -1:
            messagebox.showerror("Error", "Data tidak ditemukan untuk diedit.")
            return
            
        mhs_data = data_mahasiswa[index]

        # --- Membuat Toplevel Window (Pop-up) ---
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Data Mahasiswa NIM: {nim_to_edit}")
        edit_window.configure(bg=BG_FRAME)
        edit_window.geometry("400x300")
        
        frame_edit = tk.Frame(edit_window, bg=BG_FRAME, padx=20, pady=20)
        frame_edit.pack(expand=True, fill='both')

        # Variables for popup
        # NIM tidak bisa di edit, hanya ditampilkan
        edit_nama_var = tk.StringVar(value=mhs_data.nama)
        edit_jk_var = tk.StringVar(value=mhs_data.getJenisKelamin())
        edit_jurusan_var = tk.StringVar(value=mhs_data.getJurusan()) # Entry manual
        edit_semester_var = tk.StringVar(value=str(mhs_data.getSemester()))
        edit_ipk_var = tk.StringVar(value=str(mhs_data.getIPK()))

        # Layout di Pop-up
        tk.Label(frame_edit, text="NIM (Tidak bisa diubah)", bg=BG_FRAME).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(frame_edit, text=nim_to_edit, bg=BG_FRAME, font=FONT_BOLD).grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(frame_edit, text="Nama", bg=BG_FRAME).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame_edit, textvariable=edit_nama_var, width=25).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(frame_edit, text="Jenis Kelamin", bg=BG_FRAME).grid(row=2, column=0, sticky="w", pady=5)
        jk_frame_edit = tk.Frame(frame_edit, bg=BG_FRAME)
        jk_frame_edit.grid(row=2, column=1, sticky="w", pady=5)
        tk.Radiobutton(jk_frame_edit, text="Laki-laki", variable=edit_jk_var, value="Laki-laki", bg=BG_SOFT, selectcolor=FG_BUTTON, indicatoron=0).pack(side="left")
        tk.Radiobutton(jk_frame_edit, text="Perempuan", variable=edit_jk_var, value="Perempuan", bg=BG_SOFT, selectcolor=FG_BUTTON, indicatoron=0).pack(side="left")

        tk.Label(frame_edit, text="Jurusan", bg=BG_FRAME).grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame_edit, textvariable=edit_jurusan_var, width=25).grid(row=3, column=1, sticky="w", pady=5) # Entry manual di pop up

        tk.Label(frame_edit, text="Semester", bg=BG_FRAME).grid(row=4, column=0, sticky="w", pady=5)
        # Menggunakan Spinbox untuk semester di pop up
        spinbox_sem_edit = tk.Spinbox(frame_edit, from_=1, to_=14, width=5, textvariable=edit_semester_var)
        spinbox_sem_edit.grid(row=4, column=1, sticky="w", pady=5)

        tk.Label(frame_edit, text="IPK", bg=BG_FRAME).grid(row=5, column=0, sticky="w", pady=5)
        ttk.Entry(frame_edit, textvariable=edit_ipk_var, width=10).grid(row=5, column=1, sticky="w", pady=5)

        # Tombol Simpan Perubahan di Pop-up
        def save_edit_action():
            """Fungsi yang dipanggil saat tombol simpan di pop-up ditekan."""
            new_nama = edit_nama_var.get()
            new_jk = edit_jk_var.get()
            new_jurusan = edit_jurusan_var.get()
            new_semester_str = edit_semester_var.get()
            new_ipk_str = edit_ipk_var.get()

            # Validasi input dari pop-up (NIM sudah pasti valid)
            if not self.validate_input(nim_to_edit, new_nama, new_jurusan, new_semester_str, new_ipk_str):
                # Validasi akan menampilkan messagebox error di main window
                return

            # Update objek di list global
            mhs_data.nama = new_nama
            mhs_data.setJenisKelamin(new_jk)
            mhs_data.setJurusan(new_jurusan)
            mhs_data.setSemester(int(new_semester_str))
            mhs_data.setIPK(float(new_ipk_str))
            
            simpan_ke_file()
            self.refresh_table()
            edit_window.destroy() # Tutup pop-up setelah sukses
            messagebox.showinfo("Sukses Edit", f"Data NIM {nim_to_edit} berhasil diperbarui.")

        btn_save_edit = tk.Button(frame_edit, text="Simpan Perubahan", command=save_edit_action, bg=FG_BUTTON, fg="white", font=FONT_BOLD)
        btn_save_edit.grid(row=6, column=0, columnspan=2, pady=15)

    def logout(self):
        """Keluar dari sesi dan tampilkan layar login kembali."""
        confirm = messagebox.askyesno("Logout", "Anda yakin ingin logout?")
        if not confirm:
            return

        # Sembunyikan main window dan tampilkan login
        self.root.withdraw()
        login = LoginWindow(self.root)
        self.root.wait_window(login.top)
        if login.authenticated:
            # Jika berhasil login kembali, tampilkan kembali main window
            self.refresh_table()
            self.root.deiconify()
        else:
            # Jika batal/close di login, keluar dari aplikasi
            self.root.destroy()

# ==============================
# MAIN PROGRAM
# ==============================
if __name__ == "__main__":
    baca_dari_file()
    root = tk.Tk()
    # Mulai dengan hide root sampai login sukses
    root.withdraw()
    login = LoginWindow(root)
    root.wait_window(login.top)
    if login.authenticated:
        root.deiconify()
        app = App(root)
        root.mainloop()
    else:
        # tidak login -> keluar
        root.destroy()