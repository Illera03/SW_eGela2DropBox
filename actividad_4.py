# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
import os
import eGela
import Dropbox
import helper
import time
from urllib.parse import unquote
import tempfile
import webbrowser

##########################################################################################################

def make_entry(parent, caption, width=None, **options):
    label = tk.Label(parent, text=caption)
    label.pack(side=tk.TOP)
    entry = tk.Entry(parent, **options)
    entry.config(width=width)
    entry.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
    return entry

def make_listbox(messages_frame):
    messages_frame.config(bd=1, relief="ridge")
    scrollbar = tk.Scrollbar(messages_frame)
    msg_listbox = tk.Listbox(messages_frame, height=20, width=70, exportselection=0, selectmode=tk.EXTENDED)
    msg_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=msg_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return msg_listbox

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

def transfer_files():
    if not selected_items1:
        messagebox.showwarning("Aviso", "Selecciona al menos un PDF para transferir.")
        return
    popup, progress_var, progress_bar = helper.progress("transfer_file", "Transfering files...")
    progress = 0
    progress_var.set(progress)
    progress_bar.update()
    progress_step = float(100.0 / len(selected_items1))

    for each in selected_items1:
        idx = tree1.index(each)
        pdf_name, pdf_file = egela.get_pdf(idx)

        progress_bar.update()
        newroot.update()

        if dropbox._path == "/":
            path = "/" + unquote(pdf_name)
            print ("----------------------: "+ pdf_name)
            print("----------------------: " + unquote(pdf_name))

        else:
            path = dropbox._path + "/" + pdf_name
        dropbox.transfer_file(path, pdf_file)

        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()
        newroot.update()

        time.sleep(0.1)

    popup.destroy()
    dropbox.list_folder(msg_listbox2)
    msg_listbox2.yview(tk.END)

def delete_files():
    if not selected_items2:
        messagebox.showwarning("Aviso", "Selecciona al menos un archivo para borrar.")
        return
    
    popup, progress_var, progress_bar = helper.progress("delete_file", "Deleting files...")
    progress = 0
    progress_var.set(progress)
    progress_bar.update()
    progress_step = float(100.0 / len(selected_items2))

    for each in selected_items2:
        if dropbox._path == "/":
            path = "/" + dropbox._files[each]['name']
        else:
            path = dropbox._path + "/" + dropbox._files[each]['name']
            print (path)
        dropbox.delete_file(path)

        progress += progress_step
        progress_var.set(progress)
        progress_bar.update()

    popup.destroy()
    dropbox.list_folder(msg_listbox2)

def name_folder(folder_name):
    if dropbox._path == "/":
        dropbox._path = dropbox._path + str(folder_name)
    else:
        dropbox._path = dropbox._path + '/' + str(folder_name)
    dropbox.create_folder(dropbox._path)
    var_path.set(dropbox._path)
    dropbox._root.destroy()
    dropbox.list_folder(msg_listbox2)

def create_folder():
    popup = tk.Toplevel(newroot)
    popup.geometry('200x100')
    popup.title('Dropbox')
    popup.iconbitmap('./favicon.ico')
    helper.center(popup)

    login_frame = tk.Frame(popup, padx=10, pady=10)
    login_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(login_frame, text="Create folder")
    label.pack(side=tk.TOP)
    entry_field = tk.Entry(login_frame, width=35)
    entry_field.bind("<Return>", name_folder)
    entry_field.pack(side=tk.TOP)
    send_button = tk.Button(login_frame, text="Send", command=lambda: name_folder(entry_field.get()))
    send_button.pack(side=tk.TOP)
    dropbox._root = popup
    

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


##########################################################################################################
selected_items1 = []
selected_items2 = []
def check_credentials(event= None):
    egela.check_credentials(username, password)

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
##########################################################################################################
# Login eGela
root = tk.Tk()
root.geometry('250x150')
root.iconbitmap('./favicon.ico') #
root.title('Login eGela')
helper.center(root)
egela = eGela.eGela(root)

login_frame = tk.Frame(root, padx=10, pady=10)
login_frame.pack(fill=tk.BOTH, expand=True)

username = make_entry(login_frame, "User name:", 16)
password = make_entry(login_frame, "Password:", 16, show="*")
password.bind("<Return>", check_credentials)

button = tk.Button(login_frame, borderwidth=4, text="Login", width=10, pady=8, command=check_credentials)
button.pack(side=tk.BOTTOM)

root.mainloop()

if not egela._login:
    exit()
# Si nos logeamos en eGela cogemos las referencias a los pdfs
pdfs = egela.get_pdf_refs()

##########################################################################################################
# Login Dropbox
root = tk.Tk()
root.geometry('250x100')
root.iconbitmap('./favicon.ico')
root.title('Login Dropbox')
helper.center(root)

login_frame = tk.Frame(root, padx=10, pady=10)
login_frame.pack(fill=tk.BOTH, expand=True)
# Login and Authorize in Drobpox
dropbox = Dropbox.Dropbox(root)

label = tk.Label(login_frame, text="Login and Authorize\nin Drobpox")
label.pack(side=tk.TOP)
button = tk.Button(login_frame, borderwidth=4, text="Login", width=10, pady=8, command=dropbox.do_oauth)
button.pack(side=tk.BOTTOM)

root.mainloop()

##########################################################################################################
# eGela -> Dropbox

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
