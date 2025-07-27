import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import urllib3
import os
import sys
import webbrowser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resource_path(relative_path):
    """Retorna o caminho absoluto para o recurso, funciona no PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class UnifiSearcher:
    def __init__(self, controller, username, password):
        self.controller = controller.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False

    def login(self):
        payload = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}
        url_auth = f"{self.controller}/api/auth/login"
        r = self.session.post(url_auth, json=payload, headers=headers)
        if r.status_code == 200:
            return True
        url_auth = f"{self.controller}/api/login"
        r = self.session.post(url_auth, json=payload, headers=headers)
        return r.status_code == 200

    def get_sites(self):
        url = f"{self.controller}/api/self/sites"
        r = self.session.get(url)
        if r.status_code != 200:
            url = f"{self.controller}/proxy/network/api/self/sites"
            r = self.session.get(url)
        if r.status_code != 200:
            raise Exception("Não foi possível listar os sites.")
        return r.json().get("data", [])

    def find_device_by_mac(self, mac):
        mac = mac.lower()
        sites = self.get_sites()
        for site in sites:
            site_name = site.get("name")
            site_desc = site.get("desc") or site_name
            url = f"{self.controller}/proxy/network/api/s/{site_name}/stat/device"
            r = self.session.get(url)
            if r.status_code != 200:
                url = f"{self.controller}/api/s/{site_name}/stat/device"
                r = self.session.get(url)
            if r.status_code != 200:
                continue
            devices = r.json().get("data", [])
            for d in devices:
                if d.get("mac", "").lower() == mac:
                    return {
                        "name": d.get("name", "Sem nome"),
                        "ip": d.get("ip", "Sem IP"),
                        "model": d.get("model", "Desconhecido"),
                        "version": d.get("version", "Desconhecida"),
                        "site": site_desc
                    }
        return None

def buscar():
    controller = entry_controller.get()
    username = entry_user.get()
    password = entry_pass.get()
    mac = entry_mac.get()

    if not (controller and username and password and mac) or controller == placeholder_controller or mac == placeholder_mac:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    try:
        searcher = UnifiSearcher(controller, username, password)
        if not searcher.login():
            messagebox.showerror("Erro", "Falha no login. Verifique credenciais.")
            return

        device = searcher.find_device_by_mac(mac)
        if device:
            messagebox.showinfo(
                "Encontrado",
                f"Dispositivo encontrado!\n\n"
                f"Site: {device['site']}\n"
                f"Nome: {device['name']}\n"
                f"IP: {device['ip']}\n"
                f"Modelo: {device['model']}\n"
                f"Versão: {device['version']}"
            )
        else:
            messagebox.showinfo("Não encontrado", "Nenhum dispositivo com esse MAC.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def set_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg="grey")
    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="white")
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# --- INTERFACE ---
root = tk.Tk()
root.title("Search UNIFI MAC")
root.geometry("420x420")
root.configure(bg="#1E1E1E")

# Ícone personalizado
ico_path = resource_path("lupa.ico")
if os.path.exists(ico_path):
    root.iconbitmap(ico_path)
else:
    print("Ícone lupa.ico não encontrado.")

placeholder_controller = "https://<domain>:8443/"
placeholder_mac = "AA:BB:CC:DD:EE:FF"

label_fg = "#CCCCCC"
entry_bg = "#2D2D2D"
entry_fg = "white"
button_bg = "#3c9cdc"
button_fg = "white"

frame = tk.Frame(root, bg="#1E1E1E")
frame.pack(pady=20)

# Campos
tk.Label(frame, text="Controladora:", bg="#1E1E1E", fg=label_fg).grid(row=0, column=0, sticky="w", pady=5)
entry_controller = tk.Entry(frame, width=40, bg=entry_bg, fg=entry_fg, insertbackground="white", relief="flat")
entry_controller.grid(row=0, column=1, pady=5)
set_placeholder(entry_controller, placeholder_controller)

tk.Label(frame, text="Usuário:", bg="#1E1E1E", fg=label_fg).grid(row=1, column=0, sticky="w", pady=5)
entry_user = tk.Entry(frame, width=40, bg=entry_bg, fg=entry_fg, insertbackground="white", relief="flat")
entry_user.grid(row=1, column=1, pady=5)

tk.Label(frame, text="Senha:", bg="#1E1E1E", fg=label_fg).grid(row=2, column=0, sticky="w", pady=5)
entry_pass = tk.Entry(frame, width=40, show="*", bg=entry_bg, fg=entry_fg, insertbackground="white", relief="flat")
entry_pass.grid(row=2, column=1, pady=5)

tk.Label(frame, text="MAC Address:", bg="#1E1E1E", fg=label_fg).grid(row=3, column=0, sticky="w", pady=5)
entry_mac = tk.Entry(frame, width=40, bg=entry_bg, fg=entry_fg, insertbackground="white", relief="flat")
entry_mac.grid(row=3, column=1, pady=5)
set_placeholder(entry_mac, placeholder_mac)

# Botão
btn_buscar = tk.Button(root, text="BUSCAR", command=buscar, bg=button_bg, fg=button_fg, activebackground="#D6DED6", relief="flat", height=2, width=20)
btn_buscar.pack(pady=5)

# Logo (opcional)
logo_path = resource_path("logo_unifi.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).resize((100, 100))
    logo_tk = ImageTk.PhotoImage(logo_img)
    tk.Label(root, image=logo_tk, bg="#1E1E1E").pack(pady=5)
else:
    tk.Label(root, text="(Logo não encontrada)", bg="#1E1E1E", fg="#555555").pack(pady=10)

# --- RODAPÉ ---
def abrir_linkedin(event=None):
    webbrowser.open_new("https://www.linkedin.com/in/renan-pablo-9756293a/")

def abrir_github(event=None):
    webbrowser.open_new("https://github.com/renanpablosc")

footer_frame = tk.Frame(root, bg="#1E1E1E")
footer_frame.pack(pady=10)

# "Desenvolvido por:"
lbl_dev = tk.Label(footer_frame, text="Desenvolvido por:", bg="#1E1E1E", fg="#888888")
lbl_dev.pack()

# LinkedIn
linkedin_frame = tk.Frame(footer_frame, bg="#1E1E1E")
linkedin_frame.pack(pady=2)

linkedin_path = resource_path("linkedin.png")
if os.path.exists(linkedin_path):
    linkedin_img = Image.open(linkedin_path).resize((16, 16))
    linkedin_tk = ImageTk.PhotoImage(linkedin_img)
    lbl_icon = tk.Label(linkedin_frame, image=linkedin_tk, bg="#1E1E1E", cursor="hand2")
    lbl_icon.image = linkedin_tk
    lbl_icon.pack(side="left", padx=(0, 5))
    lbl_icon.bind("<Button-1>", abrir_linkedin)

lbl_nome = tk.Label(linkedin_frame, text="Renan Pablo", fg="#3c9cdc", bg="#1E1E1E", cursor="hand2")
lbl_nome.pack(side="left")
lbl_nome.bind("<Button-1>", abrir_linkedin)

# GitHub
github_frame = tk.Frame(footer_frame, bg="#1E1E1E")
github_frame.pack(pady=2)

github_path = resource_path("github.png")
if os.path.exists(github_path):
    github_img = Image.open(github_path).resize((40, 15))
    github_tk = ImageTk.PhotoImage(github_img)
    lbl_github_icon = tk.Label(github_frame, image=github_tk, bg="#1E1E1E", cursor="hand2")
    lbl_github_icon.image = github_tk
    lbl_github_icon.pack(side="left", padx=(0, 1))
    lbl_github_icon.bind("<Button-1>", abrir_github)

lbl_github = tk.Label(github_frame, text="renanpablsc", fg="#3c9cdc", bg="#1E1E1E", cursor="hand2")
lbl_github.pack(side="left")
lbl_github.bind("<Button-1>", abrir_github)

root.mainloop()
