# Nombre y apellidos: Jorge Illera Rivera, Bruno Izaguirre Martínez de Marañón e Iker Argulo Galán
# Asignatura y grupo: Sistemas Web, GO1
# Fecha de entrega: 09/05/2025
# Nombre de la tarea: Actividad 4: eGela2Dropbox
# Breve descripción del entregable: La aplicación eGela2Dropbox permite subir de manera selectiva los ficheros PDF del aula virtual de la asignatura Sistemas Web en eGela, 
#                                   a un directorio de Dropbox.

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
    popup, progress_var, progress_bar = helper.progress("transfer_file", "Transfering files...")
    progress = 0
    progress_var.set(progress)
    progress_bar.update()
    progress_step = float(100.0 / len(selected_items1))

    for each in selected_items1:
        pdf_name, pdf_file = egela.get_pdf(each)

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
    var.set(dropbox._path)
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

def check_credentials(event= None):
    egela.check_credentials(username, password)

def on_selecting1(event):
    global selected_items1
    widget = event.widget
    selected_items1 = widget.curselection()
    print (selected_items1)

def on_selecting2(event):
    global selected_items2
    widget = event.widget
    selected_items2 = widget.curselection()
    print (selected_items2)

def on_double_clicking2(event):
    widget = event.widget
    selection = widget.curselection()
    if selection[0] == 0 and dropbox._path != "/":
        head, tail = os.path.split(dropbox._path)
        dropbox._path = head
    else:
        selected_file = dropbox._files[selection[0]]
        if selected_file['.tag'] == 'folder':
            if dropbox._path == "/":
                dropbox._path = dropbox._path + selected_file['name']
            else:
                dropbox._path = dropbox._path + '/' + selected_file['name']
    var.set(dropbox._path)
    dropbox.list_folder(msg_listbox2)

def preview_pdf():
    if len(selected_items1) != 1:
        messagebox.showwarning("Aviso", "Selecciona un único PDF para vista previa.")
        return

    idx = selected_items1[0]
    pdf_name, pdf_data = egela.get_pdf(idx)

    tmp_path = os.path.join(tempfile.gettempdir(), pdf_name)
    with open(tmp_path, "wb") as f:
        f.write(pdf_data)

    try:
        if os.name == "nt":
            os.startfile(tmp_path)
        else:
            webbrowser.open(tmp_path)
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
newroot.geometry("850x400")
newroot.iconbitmap('./favicon.ico') #
newroot.title("eGela -> Dropbox") #
helper.center(newroot)

newroot.rowconfigure(0, weight=1)
newroot.rowconfigure(1, weight=5)
newroot.columnconfigure(0, weight=6)
newroot.columnconfigure(1, weight=1)
newroot.columnconfigure(2, weight=6)
newroot.columnconfigure(3, weight=1)

bold_font = ("Segoe UI", 10, "bold")

# Etigueta PDFs en Sistemas Web (0,0)   #
var2 = tk.StringVar()
var2.set("PDFs en Sistemas Web")
label2 = tk.Label(newroot, textvariable=var2)
label2.grid(column=0, row=0, ipadx=5, ipady=5)

# Etigueta del directorio de Dropbox (0,2)
var = tk.StringVar()
var.set(dropbox._path)
label = tk.Label(newroot, textvariable=var)
label.grid( row=0, column=2, ipadx=5, ipady=5)

# Frame con lista de PDFs e eGela (1,0)
selected_items1 = None
messages_frame1 = tk.Frame(newroot)
msg_listbox1 = make_listbox(messages_frame1)
msg_listbox1.bind('<<ListboxSelect>>', on_selecting1)
msg_listbox1.pack(side=tk.LEFT, fill=tk.BOTH)
#messages_frame1.pack()
messages_frame1.grid(row=1, column=0, ipadx=10, ipady=10, padx=2, pady=2) #

# Frame con boton >>>  y Preview
frame1 = tk.Frame(newroot)

# Botón Transfer
button1 = tk.Button(
    frame1, borderwidth=4, text=">>>", width=12, pady=8,
    bg="#9C27B0", fg="white", activebackground="#7B1FA2",
    font=bold_font, command=transfer_files
)
button1.pack(padx=2, pady=4)

# Botón Preview
button2 = tk.Button(
    frame1, borderwidth=4, text="Preview", width=12, pady=8,
    bg="#FBC02D", fg="white", activebackground="#F9A825",
    font=bold_font, command=preview_pdf
)
button2.pack(padx=2, pady=4)


frame1.grid(row=1, column=1, ipadx=5, ipady=5)

# Frame con ficheros en Dropbox
selected_items2 = None
messages_frame2 = tk.Frame(newroot)
msg_listbox2 = make_listbox(messages_frame2)
msg_listbox2.bind('<<ListboxSelect>>', on_selecting2)
msg_listbox2.bind('<Double-Button-1>', on_double_clicking2)
msg_listbox2.pack(side=tk.RIGHT, fill=tk.BOTH)

#messages_frame2.pack()
messages_frame2.grid(row=1, column=2, ipadx=10, ipady=10, padx=2, pady=2)

# Frame con botones Create, Delete, Rename file y Exit

frame2 = tk.Frame(newroot)

# Botón Delete
button2 = tk.Button(
    frame2, borderwidth=4, text="Delete", width=12, pady=8,
    bg="#ff4d4d", fg="white", activebackground="#cc0000",
    font=bold_font, command=delete_files
)
button2.pack(padx=2, pady=4)

# Botón Create folder
button3 = tk.Button(
    frame2, borderwidth=4, text="Create folder", width=12, pady=8,
    bg="#4CAF50", fg="white", activebackground="#388E3C",
    font=bold_font, command=create_folder
)
button3.pack(padx=2, pady=4)

# Botón Rename file
button_rename = tk.Button(
    frame2, borderwidth=4, text="Rename file", width=12, pady=8,
    bg="#2196F3", fg="white", activebackground="#1976D2",
    font=bold_font, command=rename_file
)
button_rename.pack(padx=2, pady=4)

# Botón Exit
button_exit = tk.Button(
    frame2, borderwidth=4, text="Exit", width=12, pady=8,
    bg="#607D8B", fg="white", activebackground="#455A64",
    font=bold_font, command=newroot.quit
)
button_exit.pack(padx=2, pady=4)

frame2.grid(row=1, column=3,  ipadx=10, ipady=10)

for each in pdfs:
    msg_listbox1.insert(tk.END, each['nombre'])
    msg_listbox1.yview(tk.END)

dropbox.list_folder(msg_listbox2)

newroot.mainloop()
