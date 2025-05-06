# Nombre y apellidos: Jorge Illera Rivera, Bruno Izaguirre Martínez de Marañón e Iker Argulo Galán
# Asignatura y grupo: Sistemas Web, GO1
# Fecha de entrega: 09/05/2025
# Nombre de la tarea: Actividad 4: eGela2Dropbox
# Breve descripción del entregable: La aplicación eGela2Dropbox permite subir de manera selectiva los ficheros PDF del aula virtual de la asignatura Sistemas Web en eGela, 
#                                   a un directorio de Dropbox.

import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'ydp70l1l4imerxn'
app_secret = 'tvg65hn7x689ygl'
server_addr = "localhost"
server_port = 8070
redirect_uri = "http://" + server_addr + ":" + str(server_port)

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None
    _msg_listbox = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        print("\n### DROPBOX ###\n")
        # por el puerto 8090 esta escuchando el servidor que generamos
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        print("\tLocal server listening on port " + str(server_port))

        # recibe la redireccio 302 del navegador
        client_connection, client_address = server_socket.accept()
        peticion = client_connection.recv(1024)
        print("\tRequest from the browser received at local server:")
        print (peticion)

        # buscar en solicitud el "auth_code"
        primera_linea =peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        print ("\tauth_code: " + auth_code)

        # devolver una respuesta al usuario
        http_response = "HTTP/1.1 200 OK\r\n\r\n" \
                        "<html>" \
                        "<head><title>Proba</title></head>" \
                        "<body>The authentication flow has completed. Close this window.</body>" \
                        "</html>"
        client_connection.sendall(http_response.encode())
        client_connection.close()
        server_socket.close()

        return auth_code

    def do_oauth(self):
        # Authorization
        servidor = 'www.dropbox.com'
        params = {'response_type': 'code', 'client_id': app_key, 'redirect_uri': redirect_uri}
        uri = 'https://' + servidor + '/oauth2/authorize?' + urllib.parse.urlencode(params)
        webbrowser.open_new(uri)

        auth_code = self.local_server()

        # Token exchange
        print('/oauth2/authorize')
        uri = 'https://api.dropboxapi.com/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {
            'code': auth_code,
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = requests.post(uri, headers=headers, data=urllib.parse.urlencode(data))
        print('\tStatus:', response.status_code)
        print('\tRespuesta:', response.text)

        contenido_json = json.loads(response.text)

        self._access_token = contenido_json['access_token']  # Ahora debería existir
        print('\tAccess Token:', self._access_token)
        self._root.destroy()

    def list_folder(self, msg_listbox):
        print("/list_folder")
        uri = "https://api.dropboxapi.com/2/files/list_folder"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        path = "" if self._path == "/" else self._path
        data = json.dumps({
            "path": path,
            "recursive": False,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False,
            "include_mounted_folders": True
        })

        response = requests.post(uri, headers=headers, data=data)
        print(f"\tStatus code: {response.status_code}")

        if response.status_code != 200:
            print("Error en la respuesta inicial:")
            print(response.text)
            return

        contenido_json = response.json()
        all_entries = contenido_json.get("entries", [])

        # Si hay más resultados, los vamos pidiendo con el cursor
        while contenido_json.get("has_more"):
            print("/list_folder/continue")
            cursor = contenido_json["cursor"]
            continue_uri = "https://api.dropboxapi.com/2/files/list_folder/continue"
            continue_data = json.dumps({"cursor": cursor})
            response = requests.post(continue_uri, headers=headers, data=continue_data)

            if response.status_code != 200:
                print("Error en la respuesta continua:")
                print(response.text)
                break

            contenido_json = response.json()
            all_entries.extend(contenido_json.get("entries", []))

        # Mostrar todo en la interfaz
        msg_listbox = helper.update_listbox2(msg_listbox, self._path, {"entries": all_entries})
        self._files = msg_listbox

    def transfer_file(self, file_path, file_data):
        print("/upload")
        uri = 'https://content.dropboxapi.com/2/files/upload'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-upload
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Dropbox-API-Arg": json.dumps({
                "path": file_path,
                "mode": "add",
                "autorename": True,
                "mute": False,
                "strict_conflict": False
            }),
            "Content-Type": "application/octet-stream"
        }

        response = requests.post(uri, headers=headers, data=file_data) 
        print("\tStatus:", response.status_code)
        print("\tRespuesta:", response.text)

    def delete_file(self, file_path):
        print("/delete_file")
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-delete
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        data = json.dumps({ "path": file_path })

        response = requests.post(uri, headers=headers, data=data)
        print("\tStatus:", response.status_code)
        print("\tRespuesta:", response.text)

    def create_folder(self, path):
        print("/create_folder")
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        # https://www.dropbox.com/developers/documentation/http/documentation#files-create_folder
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

        data = json.dumps({ "path": path, "autorename": False })

        response = requests.post(uri, headers=headers, data=data)
        print("\tStatus:", response.status_code)
        print("\tRespuesta:", response.text)

    def rename_file(self, from_path, to_path):
        print("/rename_file")
        uri = 'https://api.dropboxapi.com/2/files/move_v2'
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "from_path": from_path,
            "to_path": to_path,
            "autorename": False
        })
        response = requests.post(uri, headers=headers, data=data)
        print("\tStatus:", response.status_code)
        print("\tRespuesta:", response.text)
