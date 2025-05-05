# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote, urljoin
from bs4 import BeautifulSoup
import time
import helper
import os

class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root
        # Usamos una sesión para guardar cookies y mantener login
        self.session = requests.Session()

    def obtener_uri_enlace(self, url):
        print(f"Obteniendo página: {url}")  # Mensaje de depuración
        respuesta = self.session.get(url, allow_redirects=False)
        print(f"Status: {respuesta.status_code}")  # Depuración

        # Obtenemos la Location (URI de redirección)
        location = respuesta.headers.get("Location", "No redirección")
        location_utf8 = unquote(location)  # Decodificamos la URI

        # Extraemos el nombre del archivo (último componente de la URI)
        nombre_archivo = os.path.basename(location_utf8)
        return location_utf8, nombre_archivo

    # Función para extraer enlaces por /mod/resource en el link
    def obtener_enlaces_resource(self, url):
        """Extrae enlaces de recursos desde una página."""
        print(f"Extrayendo recursos de: {url}")  # Depuración
        respuesta = self.session.get(url)
        print(f"Status: {respuesta.status_code}")  # Depuración
        if respuesta.status_code != 200:
            return []

        soup = BeautifulSoup(respuesta.text, "html.parser")
        enlaces = [
            urljoin("https://egela.ehu.eus", a["href"])
            for a in soup.find_all("a", href=True)
            if "/mod/resource" in a["href"]
        ]
        print(f"{len(enlaces)} recursos encontrados")  # Depuración
        return enlaces

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICIÓN #####")
        login_url = "https://egela.ehu.eus/login/index.php"
        r1 = self.session.get(login_url, allow_redirects=True)
        print(f"Status: {r1.status_code} | URL final: {r1.url}")
        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 2. EXTRAER TOKEN #####")
        soup1 = BeautifulSoup(r1.text, "html.parser")
        form = soup1.find("form", action=True)
        if not form:
            popup.destroy()
            messagebox.showerror("Login Error", f"No se encontró formulario en {r1.url}")
            return
        action = form["action"]
        if not action.startswith("http"):
            action = urljoin(r1.url, action)
        # Recogemos todos los campos hidden
        data = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            if name:
                data[name] = inp.get("value", "")
        print(f"Campos ocultos obtenidos: {list(data.keys())}")
        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 3. PETICIÓN LOGIN #####")
        data["username"] = username.get()
        data["password"] = password.get()
        print(f'POST a: {action} con data keys: {list(data.keys())}')
        r2 = self.session.post(action, data=data, allow_redirects=True)
        print(f"Status: {r2.status_code} | URL final: {r2.url}")
        progress = 75
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        # Validamos que no seguimos en login
        if "login/index.php" in r2.url:
            popup.destroy()
            messagebox.showerror("Login failed", "Usuario o contraseña incorrectos.")
            return

        print("\n##### 4. BUSCAR CURSO #####")
        soup2 = BeautifulSoup(r2.text, "html.parser")
        for enlace in soup2.find_all('a', href=True):
            if "Sistemas Web" in enlace.get_text():
                href = enlace['href']
                self._curso = href if href.startswith("http") else urljoin(r2.url, href)
                print(f"Curso encontrado: {self._curso}")
                break
        else:
            popup.destroy()
            messagebox.showerror("Login Error", "No se encontró el enlace a Sistemas Web.")
            return

        progress = 100
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)
        popup.destroy()

        self._login = 1
        self._root.destroy()

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 5. PETICIÓN Página principal de la asignatura #####")
        r = self.session.get(self._curso)
        print(f"Status: {r.status_code} | URL: {r.url}")
        soup = BeautifulSoup(r.text, "html.parser")

        # Crear diccionario de secciones
        sections = {}
        tabs = soup.select(".nav.nav-tabs .nav-item a.nav-link")
        for tab in tabs:
            title = tab.get_text().strip()
            link = tab.get("href")
            if link and "&section" in link:
                sections[title] = link
        num = len(sections) or 1
        step = 100.0 / num
        print(f"Secciones encontradas: {list(sections.keys())}")

        enlaces_recursos = []
        for nombre, url in sections.items():
            print(f"\nSección: {nombre}")
            recursos = self.obtener_enlaces_resource(url)
            for recurso in recursos:
                uri, nombre_archivo = self.obtener_uri_enlace(recurso)
                if uri.lower().endswith(".pdf"):
                    # HEAD para obtener tamaño
                    head = self.session.head(uri, allow_redirects=True)
                    size_b = int(head.headers.get("Content-Length", 0))
                    size_mb = size_b / (1024**2)
                    enlaces_recursos.append({
                        "uri": uri,
                        "nombre": nombre_archivo,
                        "size": size_mb
                    })
                    print(f"PDF añadido: {nombre_archivo} ({size_mb:.2f} MB)")
            progress += step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)

        popup.destroy()
        self._refs = enlaces_recursos
        print(f"\nTotal PDFs encontrados: {len(enlaces_recursos)}")
        return self._refs

    def get_pdf(self, selection):
        print("\t##### Descargando PDF seleccionado #####")
        pdf_obj = self._refs[selection]
        base = pdf_obj['nombre']
        pdf_name = base if base.lower().endswith(".pdf") else base + ".pdf"
        print(f"Nombre final: {pdf_name}")
        print(f"URL: {pdf_obj['uri']}")

        r = self.session.get(pdf_obj["uri"], allow_redirects=True, stream=True)
        print(f"Status: {r.status_code}")
        r.raise_for_status()

        content = bytearray()
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                content.extend(chunk)
        print(f"Tamaño descargado: {len(content)} bytes")

        return pdf_name, bytes(content)
