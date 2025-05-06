# -*- coding: UTF-8 -*-
from tkinter import messagebox
import requests
import urllib
from urllib.parse import unquote
from bs4 import BeautifulSoup
import time
import helper
from urllib.parse import urljoin
import os


class eGela:
    _login = 0
    _cookie = ""
    _curso = ""
    _refs = []
    _root = None

    def __init__(self, root):
        self._root = root

    def obtener_uri_enlace(self, url):
        print(f"Obteniendo página: {url}")  # Mensaje de depuración
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        respuesta = requests.get(url, headers=cabeceras, allow_redirects=False)
        print("Página obtenida correctamente")  # Mensaje de depuración

        # Obtenemos la Location (URI de redirección)
        location = respuesta.headers.get("Location", "No redirección")
        location_utf8 = urllib.parse.unquote(location)  # Decodificamos la URI

        # Extraemos el nombre del archivo (último componente de la URI)
        nombre_archivo = os.path.basename(location_utf8)

        # Extraemos el nombre del archivo (último componente de la URI)
        nombre_archivo = os.path.basename(location_utf8)

        # Eliminar la extensión .pdf si está presente
        if nombre_archivo.lower().endswith('.pdf'):
            nombre_archivo = nombre_archivo[:-4]  # Quita los últimos 4 caracteres

        return location_utf8, nombre_archivo

    # Función para extraer enlaces por /mod/resource en el link
    def obtener_enlaces_resource(self, url):
        """Extrae enlaces de recursos desde una página."""
        respuesta = requests.request('GET', url, headers={'Host': 'egela.ehu.eus', 'Cookie': self._cookie})
        if respuesta.status_code != 200:
            return []

        soup = BeautifulSoup(respuesta.text, "html.parser")
        return [urljoin("https://egela.ehu.eus", a["href"]) for a in soup.find_all("a", href=True) if
                "/mod/resource" in a["href"]]

    def check_credentials(self, username, password, event=None):
        popup, progress_var, progress_bar = helper.progress("check_credentials", "Logging into eGela...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("##### 1. PETICIÓN #####")
        metodo = 'GET'
        uri = "https://egela.ehu.eus/login/index.php"
        cabeceras = {'Host': 'egela.ehu.eus'}
        cuerpo = ''
        print(f'Método: {metodo} | URI: {uri}')
        print(f'Cuerpo: {cuerpo}')
        respuesta = requests.request(metodo, uri, data=cuerpo, allow_redirects=False)
        cookies_dict = respuesta.cookies.get_dict()
        cookies_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
        _cookie = unquote(cookies_str)
        print(f'Status code: {respuesta.status_code} | Descripción: {respuesta.reason}')
        print(f'Location: {respuesta.headers.get("Location", "No redirección")} | Cookie: {_cookie}')
        print("-" * 120)

        progress = 25
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        print("\n##### 2. PETICIÓN #####")
        metodo = 'POST'
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': _cookie,
                     'Content-Type': 'application/x-www-form-urlencoded'}
        print(f'Método: {metodo} | URI: {uri}')
        print(f'Cuerpo: {cuerpo}')
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)
        print(f'Status code: {respuesta.status_code} | Descripción: {respuesta.reason}')
        print(f'Location: {respuesta.headers.get("Location", "No redirección")} | Cookie: {_cookie}')
        print("-" * 120)
        # Extraer el logintoken con BeautifulSoup
        soup = BeautifulSoup(respuesta.text, "html.parser")
        token_input = soup.find("input", {"name": "logintoken"})
        logintoken = token_input["value"] if token_input else None
        print(f"Logintoken extraído: {logintoken}")
        metodo = 'POST'
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': _cookie,
                     'Content-Type': 'application/x-www-form-urlencoded'}
        cuerpo = f'logintoken={logintoken}&username={str(username.get())}&password={str(password.get())}'
        print(f'Método: {metodo} | URI: {uri}')
        print(f'Cuerpo: {cuerpo}')
        respuesta = requests.request(metodo, uri, headers=cabeceras, data=cuerpo, allow_redirects=False)
        print(f'Status code: {respuesta.status_code} | Descripción: {respuesta.reason}')
        print(f'Location: {respuesta.headers.get("Location", "No redirección")} | Cookie: {_cookie}')
        print("-" * 120)
        cookies_dict = respuesta.cookies.get_dict()
        _cookie = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
        _cookie = unquote(_cookie)
        loginComprobar = respuesta.headers.get("Location", "No redirección")
        progress = 50
        progress_var.set(progress)
        progress_bar.update()
        time.sleep(1)

        if "testsession" in str(loginComprobar):
            print("\n##### 3. PETICIÓN #####")
            metodo = 'GET'
            uri = respuesta.headers["Location"]
            cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': _cookie}
            print(f'Método: {metodo} | URI: {uri}')
            respuesta = requests.request(metodo, uri, headers=cabeceras, data='', allow_redirects=False)
            print(f'Status code: {respuesta.status_code} | Descripción: {respuesta.reason}')
            print(f'Location: {respuesta.headers.get("Location", "No redirección")} | Cookie: {_cookie}')
            print("-" * 120)
            progress = 75
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(1)
            popup.destroy()

            print("\n##### 4. PETICION #####")
            metodo = 'GET'
            uri = respuesta.headers["Location"]
            cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': _cookie}
            print(f'Método: {metodo} | URI: {uri}')
            respuesta = requests.request(metodo, uri, headers=cabeceras, data='', allow_redirects=False)
            print(f'Status code: {respuesta.status_code} | Descripción: {respuesta.reason}')
            print(f'Location: {respuesta.headers.get("Location", "No redirección")} | Cookie: {_cookie}')
            print("-" * 120)
            progress = 100
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(1)
            popup.destroy()

        if "testsession" in str(loginComprobar):
            self._login = 1
            self._cookie = _cookie
            html = BeautifulSoup(respuesta.text, "html.parser")
            asignatura = "Sistemas Web"
            # buscar uri de sistemas web
            for enlace in html.find_all('a'):
                if enlace.string and asignatura in enlace.get_text():
                    uri = enlace.get('href', 'No disponible')
            self._curso = uri
            self._root.destroy()
        else:
            messagebox.showinfo("Alert Message", "Login incorrect!")
            exit(0)

    def get_pdf_refs(self):
        popup, progress_var, progress_bar = helper.progress("get_pdf_refs", "Downloading PDF list...")
        progress = 0
        progress_var.set(progress)
        progress_bar.update()

        print("\n##### 4. PETICIÓN (Página principal de la asignatura en eGela) #####")
        metodo = 'GET'
        cabeceras = {'Host': 'egela.ehu.eus', 'Cookie': self._cookie}
        print(f'Método: {metodo} | URI: {self._curso}')
        respuestaSW = requests.request(metodo, self._curso, headers=cabeceras, data='', allow_redirects=False)
        print(f'Status code: {respuestaSW.status_code} | Descripción: {respuestaSW.reason}')
        print("-" * 120)
        soup = BeautifulSoup(respuestaSW.text, "html.parser")
        # Crear diccionario
        sections = {}
        tabs = soup.select(".nav.nav-tabs .nav-item a.nav-link")

        for tab in tabs:
            title = tab.contents[0].strip()  # obtiene el nombre de la sección
            link = tab.get("href")
            if link and "&section" in link:
                sections[title] = link  # mete el link de la sección
        num_secciones_eGela = len(sections)
        progress_step = float(100.0 / num_secciones_eGela)

        print("\n##### Analisis del HTML... #####")
        # Buscar las pestañas de navegación

        print(sections)  # Imprime el diccionario con los títulos y enlaces
        enlaces_recursos = []
        for nombre, url in sections.items():  # por cada seccion
            print(f"Sección: {nombre}")
            recursos = self.obtener_enlaces_resource(url)  # Esto devuelve una lista de URLs de la seccion
            for recurso in recursos:  # Iteramos sobre cada enlace individualmente
                uri, nombre_archivo = self.obtener_uri_enlace(recurso)
                if uri and uri.endswith(".pdf"):
                    size_mb = None
                    try:
                        # Obtenemos tamaño con HEAD request
                        response = requests.head(uri, allow_redirects=True)
                        if 'Content-Length' in response.headers:
                            size_bytes = int(response.headers['Content-Length'])
                            size_mb = size_bytes / (1024 * 1024)
                    except Exception as e:
                        print(f"No se pudo obtener el tamaño de {uri}: {e}")
                    enlaces_recursos.append({
                        "uri": recurso,
                        "nombre": nombre_archivo,
                        "size": size_mb if size_mb is not None else 0
                    })
            progress_step = float(100.0 / num_secciones_eGela)
            progress += progress_step
            progress_var.set(progress)
            progress_bar.update()
            time.sleep(0.1)
            print(f" {len(recursos)} enlaces encontrados.")
        self._refs = enlaces_recursos
        print(enlaces_recursos)
        popup.destroy()
        return self._refs

    def get_pdf(self, selection):

        print("\t##### Descargando  PDF... #####")
        cabeceras = {
            'Cookie': self._cookie
        }
        pdf_object = self._refs[selection]
        pdf_name = pdf_object['nombre'] + ".pdf"
        pdf = pdf_object['uri']
        pdf_response = requests.request('GET', pdf, headers=cabeceras, allow_redirects=False)
        print(f'Status code: {pdf_response.status_code}')
        print(f'Reason: {pdf_response.reason}')
        location = pdf_response.headers.get("Location", "No redirección")
        location_utf8 = urllib.parse.unquote(location)  # Decodificamos la URI
        print(location_utf8)
        pdf_link = requests.request('GET', location_utf8, headers=cabeceras, allow_redirects=False, stream=True)
        print(f'Status code: {pdf_link.status_code}')
        print(f'Reason: {pdf_link.reason}')
        pdf_content = pdf_link.content

        return pdf_name, pdf_content