import tkinter as tk
from tkinter import ttk

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()
    win.update_idletasks()

def progress(tipo, title):
    if tipo == "get_pdf_refs":
        popup = tk.Tk()
    else:
        popup = tk.Toplevel()
    popup.geometry('250x50')
    popup.title(title)
    popup.iconbitmap('./favicon.ico')
    center(popup)
    label = tk.Label(popup, text=title)
    label.grid(row=0, column=0)
    label.pack(side=tk.TOP)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100)
    #progress_bar.grid(row=1, column=0)
    progress_bar.pack(side=tk.TOP)

    return popup, progress_var, progress_bar

def update_listbox2(msg_listbox, path, edukia_json):
    msg_listbox = msg_listbox
    msg_listbox.delete(0, tk.END)

    files = []
    if path != '/':
        files.append({'id': 'parent',
                            'name': "..",
                            '.tag': "folder"})
        msg_listbox.insert(tk.END, "..")
        msg_listbox.itemconfigure(tk.END, background="red")

    for each in edukia_json['entries']:
        msg_listbox.insert(tk.END, each['name'])
        if each['.tag'] == "folder":
            msg_listbox.itemconfigure(tk.END, background="darkgrey")
        files.append({'id': each['id'],
                            'name': each['name'],
                            '.tag': each['.tag']})
    return files
