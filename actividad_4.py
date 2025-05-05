# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import os
import tempfile
import webbrowser
from urllib.parse import unquote

import eGela
import Dropbox
import helper
import time

##########################################################################################################

def make_entry(parent, caption, width=None, **options):
    label = tk.Label(parent, text=caption)
    label.pack(side=tk.TOP)
    entry = tk.Entry(parent, **options)
    entry.config(width=width)
    entry.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
    return entry

def make_listbox(parent):
    parent.config(bd=1, relief="ridge")
    scrollbar = tk.Scrollbar(parent)
    lst = tk.Listbox(parent,
                      height=20,
                      width=40,
                      exportselection=0,
                      selectmode=tk.EXTENDED)
    lst.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=lst.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return lst

def make_treeview(parent):
    """
    Treeview con dos columnas: Nombre y Tamaño (MB).
    - Nombre: ancho inicial 300px, estirable.
    - Tamaño: ancho fijo 200px, no estirable.
    """
    parent.config(bd=1, relief="ridge")
    cols = ("nombre", "size")
    tree = ttk.Treeview(parent, columns=cols, show="headings", height=20)

    tree.heading("nombre", text="Nombre")
    tree.heading("size",   text="Tamaño (MB)")

    tree.column("nombre", width=300, minwidth=200, anchor="w", stretch=True)
    tree.column("size",   width=200, minwidth=200, anchor="e", stretch=False)

    vsb = tk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)

    return tree

##########################################################################################################
# Variables de selección
selected_items1 = []
selected_items2 = []

def on_select_tree(event):
    global selected_items1
    selected_items1 = tree1.selection()

def on_select_list2(event):
    global selected_items2
    selected_items2 = msg_listbox2.curselection()

def on_double_click_list2(event):
    sel = msg_listbox2.curselection()
    if not sel:
        return
    idx = sel[0]
    name = dropbox._files[idx]['name']
    # Subir a la carpeta padre
    if name in ('..', '...'):
        parent = os.path.dirname(dropbox._path.rstrip('/'))
        dropbox._path = parent if parent else '/'
    else:
        entry = dropbox._files[idx]
        # Navegar solo si es carpeta
        if entry.get('.tag') == 'folder':
            dropbox._path = (dropbox._path.rstrip('/') + '/' + name) if dropbox._path != '/' else '/' + name
        else:
            return
    dropbox.list_folder(msg_listbox2)

def preview_pdf():
    if len(selected_items1) != 1:
        messagebox.showwarning("Aviso", "Selecciona un único PDF para vista previa.")
        return

    idx = tree1.index(selected_items1[0])
    pdf_name, pdf_data = egela.get_pdf(idx)

    tmp = os.path.join(tempfile.gettempdir(), pdf_name)
    with open(tmp, "wb") as f:
        f.write(pdf_data)

    try:
        if os.name == "nt":
            os.startfile(tmp)
        else:
            webbrowser.open(tmp)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el PDF: {e}")

def transfer_files():
    if not selected_items1:
        messagebox.showwarning("Aviso", "Selecciona al menos un PDF para transferir.")
        return

    popup, var, bar = helper.progress("transfer_file", "Transfiriendo archivos...")
    progreso = 0
    step = 100.0 / len(selected_items1)

    for item in selected_items1:
        idx = tree1.index(item)
        nombre, data = egela.get_pdf(idx)
        path = ("/" if dropbox._path == "/" else dropbox._path + "/") + unquote(nombre)
        dropbox.transfer_file(path, data)
        progreso += step
        var.set(progreso)
        bar.update()

    popup.destroy()
    dropbox.list_folder(msg_listbox2)

def delete_files():
    if not selected_items2:
        messagebox.showwarning("Aviso", "Selecciona al menos un archivo para borrar.")
        return

    popup, var, bar = helper.progress("delete_file", "Borrando archivos...")
    progreso = 0
    step = 100.0 / len(selected_items2)

    for idx in selected_items2:
        name = dropbox._files[idx]['name']
        path = ("/" if dropbox._path == "/" else dropbox._path + "/") + name
        dropbox.delete_file(path)
        progreso += step
        var.set(progreso)
        bar.update()

    popup.destroy()
    dropbox.list_folder(msg_listbox2)

def rename_file():
    if len(selected_items2) != 1:
        messagebox.showerror("Error", "Selecciona exactamente 1 archivo para renombrar.")
        return

    idx = selected_items2[0]
    old = dropbox._files[idx]['name']
    if not old.lower().endswith(".pdf"):
        messagebox.showerror("Error", "Solo archivos .pdf.")
        return

    popup = tk.Toplevel(newroot)
    popup.title("Rename file")
    helper.center(popup)
    tk.Label(popup, text=f"Renombrar '{old}' a:").pack(pady=5)
    entry = tk.Entry(popup, width=40)
    entry.insert(0, old[:-4])
    entry.pack(pady=5)

    def do_rename():
        new_name = entry.get().strip() + ".pdf"
        base = "" if dropbox._path == "/" else dropbox._path
        dropbox.rename_file(base + "/" + old, base + "/" + new_name)
        popup.destroy()
        dropbox.list_folder(msg_listbox2)

    tk.Button(popup, text="OK", command=do_rename).pack(pady=5)
    popup.transient(newroot)
    entry.focus()

def create_folder():
    popup = tk.Toplevel(newroot)
    popup.title("Create folder")
    helper.center(popup)

    frame = tk.Frame(popup, padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Nombre de la carpeta:").pack(pady=(0,5))
    entry = tk.Entry(frame, width=30)
    entry.pack(pady=(0,5))
    entry.bind("<Return>", lambda e: name_folder(entry.get()))

    # ↓ aquí reduje el espacio vertical del botón para subirlo más
    tk.Button(frame, text="Crear", width=10, command=lambda: name_folder(entry.get())).pack(pady=(0,2))

    dropbox._root = popup

def name_folder(name):
    if not name.strip():
        return
    newp = ("/" if dropbox._path == "/" else dropbox._path + "/") + name.strip()
    dropbox.create_folder(newp)
    dropbox._root.destroy()
    var_path.set(newp)
    dropbox._path = newp
    dropbox.list_folder(msg_listbox2)

##########################################################################################################
# — LOGIN eGELA —
root = tk.Tk()
root.geometry("250x150")
root.iconbitmap("./favicon.ico")
root.title("Login eGela")
helper.center(root)

egela = eGela.eGela(root)
frm = tk.Frame(root, padx=10, pady=10)
frm.pack(fill=tk.BOTH, expand=True)

username = make_entry(frm, "User name:", 16)
password = make_entry(frm, "Password:", 16, show="*")
password.bind("<Return>", lambda e: egela.check_credentials(username, password))

tk.Button(frm, text="Login", width=10,
          command=lambda: egela.check_credentials(username, password))\
  .pack(side=tk.BOTTOM, pady=5)

root.mainloop()
if not egela._login:
    exit()

pdfs = egela.get_pdf_refs()

##########################################################################################################
# — LOGIN DROPBOX —
root2 = tk.Tk()
root2.geometry("250x100")
root2.iconbitmap("./favicon.ico")
root2.title("Login Dropbox")
helper.center(root2)

dropbox = Dropbox.Dropbox(root2)
frm2 = tk.Frame(root2, padx=10, pady=10)
frm2.pack(fill=tk.BOTH, expand=True)

tk.Label(frm2, text="Login and Authorize\nin Dropbox").pack()
msg_btn = tk.Button(frm2, text="Login", width=10, command=dropbox.do_oauth)
msg_btn.pack(side=tk.BOTTOM, pady=5)
root2.mainloop()

##########################################################################################################
# — INTERFAZ PRINCIPAL —
newroot = tk.Tk()
newroot.geometry("1000x450")
newroot.iconbitmap("./favicon.ico")
newroot.title("eGela -> Dropbox")
helper.center(newroot)

# Estilo suave
style = ttk.Style(newroot)
style.configure("Treeview", font=("Segoe UI", 9))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# Grid layout
newroot.rowconfigure(0, weight=1)
newroot.rowconfigure(1, weight=5)
newroot.rowconfigure(2, weight=0)
newroot.columnconfigure(0, weight=6)
newroot.columnconfigure(1, weight=1)
newroot.columnconfigure(2, weight=6)
newroot.columnconfigure(3, weight=1)

# Etiquetas
tk.Label(newroot, text="PDFs en Sistemas Web").grid(row=0, column=0, padx=5, pady=5)
var_path = tk.StringVar(value=dropbox._path)
tk.Label(newroot, textvariable=var_path).grid(row=0, column=2, padx=5, pady=5)

# Treeview eGela
frame1 = tk.Frame(newroot)
tree1 = make_treeview(frame1)
tree1.bind("<<TreeviewSelect>>", on_select_tree)
tree1.pack(fill=tk.BOTH, expand=True)
frame1.grid(row=1, column=0, padx=2, pady=2)

# Botones Transfer & Preview
btns = tk.Frame(newroot)
tk.Button(btns, text=">>>", width=10, command=transfer_files).pack(pady=5)
tk.Button(btns, text="Preview", width=10, command=preview_pdf).pack(pady=5)
btns.grid(row=1, column=1, padx=2, pady=2)

# Listbox Dropbox
frame2 = tk.Frame(newroot)
msg_listbox2 = make_listbox(frame2)
msg_listbox2.bind("<<ListboxSelect>>", on_select_list2)
msg_listbox2.bind('<Double-Button-1>', on_double_click_list2)
msg_listbox2.pack(fill=tk.BOTH, expand=True)
frame2.grid(row=1, column=2, padx=2, pady=2)

# Botones acciones Dropbox
frame3 = tk.Frame(newroot)
tk.Button(frame3, bg="orange", text="Delete", width=10, command=delete_files).pack(pady=2)
tk.Button(frame3, bg="blue", text="Rename", width=10, command=rename_file).pack(pady=2)
tk.Button(frame3, text="Create folder", width=10, command=create_folder).pack(pady=2)
tk.Button(frame3, bg="red", text="Exit", width=10, command=newroot.destroy).pack(pady=2)
frame3.grid(row=1, column=3, padx=2, pady=2)

# Footer centrado
footer = tk.Label(
    newroot,
    text="Gracias por usar nuestro programa",
    bg=newroot.cget("bg"),
    fg="gray"
)
footer.grid(row=2, column=0, columnspan=4, sticky="s", pady=5)

# Cargar PDFs con tamaño
for p in pdfs:
    tree1.insert("", tk.END, values=(p["nombre"], f"{p['size']:.2f} MB"))
tree1.yview_moveto(1.0)

# Listar Dropbox inicialmente
dropbox.list_folder(msg_listbox2)

newroot.mainloop()
