import os
import platform
import random
import tkinter as tk
from tkinter import messagebox

# Daftar buah rahasia
DAFTAR_BUAH = ["apel", "mangga", "pisang", "semangka", "anggur", "durian"]
secret_fruit = random.choice(DAFTAR_BUAH)


def shutdown_pc():
  current_os = platform.system()
  if current_os == "Windows":
    os.system("shutdown /s /t 5")
  elif current_os == "Linux" or current_os == "Darwin":
    os.system("sudo shutdown now")


def cek_tebakan():
  global secret_fruit
  tebakan = entry_tebakan.get().strip().lower()

  if not tebakan:
    messagebox.showwarning("Peringatan", "Nama buah tidak boleh kosong!")
    return

  if tebakan == secret_fruit:
    messagebox.showinfo(
        "Selamat!",
        f"Tebakanmu BENAR! ({secret_fruit}). PC kamu selamat dari"
        " kehancuran!",
    )
    root.destroy()
  else:
    messagebox.showerror(
        "Game Over!",
        f"SALAH! Buah yang benar adalah '{secret_fruit}'. PC akan dimatikan"
        " dalam 5 detik!",
    )
    shutdown_pc()
    root.destroy()


# Membuat Jendela Utama (GUI Window)
root = tk.Tk()
root.title("Fruit of Doom - Desktop Edition")
root.geometry("450x300")
root.config(bg="#12141c")

# Label Judul
label_judul = tk.Label(
    root,
    text="🍎 FRUIT OF DOOM 🍌",
    font=("Arial", 18, "bold"),
    fg="#ff3366",
    bg="#12141c",
)
label_judul.pack(pady=15)

# Label Petunjuk
petunjuk_text = (
    "Pilihan Buah:\n[apel, mangga, pisang, semangka, anggur, durian]\n\n⚠️"
    " SALAH TEBAK = PC AKAN CRASHH"
)
label_info = tk.Label(
    root,
    text=petunjuk_text,
    font=("Arial", 11),
    fg="#e0e0e0",
    bg="#12141c",
    justify="center",
)
label_info.pack(pady=5)

# Kotak Input Teks
entry_tebakan = tk.Entry(
    root, font=("Arial", 14), justify="center", bd=2, relief="solid"
)
entry_tebakan.pack(pady=15, ipadx=10, ipady=5)

# Tombol Kirim Tebakan
btn_tebak = tk.Button(
    root,
    text="TEBAK SEKARANG",
    font=("Arial", 12, "bold"),
    bg="#ff3366",
    fg="white",
    activebackground="#ff194d",
    activeforeground="white",
    padx=10,
    pady=5,
    command=cek_tebakan,
)
btn_tebak.pack(pady=10)

# Menjalankan aplikasi
root.mainloop()