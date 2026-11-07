# ------------------------------------------------------------
# 💧 Control de lámpara con Arduino por USB
# 💜 Interfaz bonita en Tkinter + ttkbootstrap (redimensionable y con degradado en todo)
# ------------------------------------------------------------

import serial
import serial.tools.list_ports
import threading
import time
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

arduino = None
conectado = False
puerto = ""
baudrate = 9600

def listar_puertos():
    puertos = serial.tools.list_ports.comports()
    lista = [p.device for p in puertos]
    combo_puertos["values"] = lista
    if lista:
        combo_puertos.current(0)

def conectar():
    global arduino, conectado, puerto
    puerto = combo_puertos.get()
    try:
        arduino = serial.Serial(puerto, baudrate, timeout=1)
        conectado = True
        lbl_estado.config(text="✅ Conectado", bootstyle="success")
        agregar_notificacion("🔌 Conectado al Arduino")
        threading.Thread(target=escuchar_arduino, daemon=True).start()
    except:
        messagebox.showerror("Error", "No se pudo conectar al Arduino")
        lbl_estado.config(text="❌ Desconectado", bootstyle="danger")
        conectado = False

def desconectar():
    global arduino, conectado
    if conectado:
        arduino.close()
        conectado = False
        lbl_estado.config(text="❌ Desconectado", bootstyle="danger")
        agregar_notificacion("🔌 Arduino desconectado")

def enviar_comando(cmd):
    if conectado:
        try:
            arduino.write(cmd.encode())
            if cmd == "1":
                agregar_notificacion("💡 Lámpara encendida (5 min manual)")
            elif cmd == "0":
                agregar_notificacion("⛔ Lámpara apagada (manual)")
            elif cmd == "A":
                agregar_notificacion("⚙ Modo automático activado")
        except:
            agregar_notificacion("⚠ Error enviando comando")
    else:
        messagebox.showwarning("Aviso", "No hay conexión con el Arduino")

def escuchar_arduino():
    global conectado
    while conectado:
        try:
            if arduino.in_waiting > 0:
                mensaje = arduino.readline().decode().strip()
                if mensaje:
                    agregar_notificacion("💧 " + mensaje)
            time.sleep(0.1)
        except:
            break

def agregar_notificacion(texto):
    lista_notificaciones.insert(0, texto)
    if lista_notificaciones.size() > 50:
        lista_notificaciones.delete(50, tk.END)

def redibujar_fondo(event=None):
    canvas_bg.delete("all")
    width = root.winfo_width()
    height = root.winfo_height()
    # Degradado morado-azul
    for i in range(height):
        r = min(100 + i // 3, 255)
        g = min(90 + i // 4, 255)
        b = min(150 + i // 2, 255)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas_bg.create_line(0, i, width, i, fill=color)
    # Gotitas decorativas
    for x in range(30, width, 80):
        canvas_bg.create_oval(x, 40, x+10, 55, fill="#a29bfe", outline="")

# ------------------------------------------------------------
# 🎨 Interfaz
# ------------------------------------------------------------
root = ttk.Window(themename="cosmo")
root.title("💧 Control de Lámpara - USB")
root.geometry("500x600")
root.resizable(True, True)

# Canvas de fondo degradado
canvas_bg = tk.Canvas(root, highlightthickness=0)
canvas_bg.pack(fill="both", expand=True)
root.bind("<Configure>", redibujar_fondo)

# Contenedor transparente encima del Canvas
main_frame = ttk.Frame(canvas_bg, padding=10, bootstyle="secondary")
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

lbl_estado = ttk.Label(main_frame, text="❌ Desconectado", font=("Arial", 16))
lbl_estado.pack(pady=10)

frame_puerto = ttk.Frame(main_frame)
frame_puerto.pack(pady=5)
ttk.Label(frame_puerto, text="Puerto COM:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
combo_puertos = ttk.Combobox(frame_puerto, font=("Arial", 12), width=10)
combo_puertos.pack(side=tk.LEFT, padx=5)
btn_refresh = ttk.Button(frame_puerto, text="🔄", command=listar_puertos, bootstyle="secondary")
btn_refresh.pack(side=tk.LEFT)

frame_con = ttk.Frame(main_frame)
frame_con.pack(pady=5)
ttk.Button(frame_con, text="Conectar", command=conectar, bootstyle="success").pack(side=tk.LEFT, padx=5)
ttk.Button(frame_con, text="Desconectar", command=desconectar, bootstyle="danger").pack(side=tk.LEFT, padx=5)

frame_ctrl = ttk.Frame(main_frame)
frame_ctrl.pack(pady=10, fill="x")
ttk.Button(frame_ctrl, text="💡 Encender 5 min", command=lambda: enviar_comando("1"), bootstyle="purple").pack(fill="x", pady=5)
ttk.Button(frame_ctrl, text="⛔ Apagar", command=lambda: enviar_comando("0"), bootstyle="purple").pack(fill="x", pady=5)
ttk.Button(frame_ctrl, text="⚙ Automático", command=lambda: enviar_comando("A"), bootstyle="purple").pack(fill="x", pady=5)

ttk.Label(main_frame, text="📜 Notificaciones:", font=("Arial", 12)).pack(pady=5)
lista_notificaciones = tk.Listbox(main_frame, font=("Arial", 10), bg="#f0f0ff", fg="#333")
lista_notificaciones.pack(fill="both", expand=True, pady=5)

listar_puertos()
root.mainloop()