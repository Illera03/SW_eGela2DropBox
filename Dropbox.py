import requests
import urllib
import webbrowser
from socket import AF_INET, socket, SOCK_STREAM
import json
import helper

app_key = 'bso6v4ow9k7djyb'
app_secret = '1ephv683ygzj4xe'
server_addr = "localhost"
server_port = 8070
redirect_uri = f"http://{server_addr}:{server_port}"

class Dropbox:
    _access_token = ""
    _path = "/"
    _files = []
    _root = None

    def __init__(self, root):
        self._root = root

    def local_server(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((server_addr, server_port))
        server_socket.listen(1)
        client_connection, _ = server_socket.accept()
        peticion = client_connection.recv(1024)
        primera_linea = peticion.decode('UTF8').split('\n')[0]
        aux_auth_code = primera_linea.split(' ')[1]
        auth_code = aux_auth_code[7:].split('&')[0]
        client_connection.sendall(
            b"HTTP/1.1 200 OK\r\n\r\n<html><body>Auth complete. Close window.</body></html>"
        )
        client_connection.close()
        server_socket.close()
        return auth_code

    def do_oauth(self):
        params = {
            'response_type': 'code',
            'client_id': app_key,
            'redirect_uri': redirect_uri
        }
        uri = 'https://www.dropbox.com/oauth2/authorize?' + urllib.parse.urlencode(params)
        webbrowser.open_new(uri)

        auth_code = self.local_server()

        token_uri = 'https://api.dropboxapi.com/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'code': auth_code,
            'client_id': app_key,
            'client_secret': app_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_uri, headers=headers, data=urllib.parse.urlencode(data))
        contenido = response.json()
        self._access_token = contenido.get('access_token', '')
        self._root.destroy()

    def list_folder(self, msg_listbox):
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
        if response.status_code != 200:
            print("Error:", response.text)
            return
        contenido = response.json()
        entries = contenido.get("entries", [])
        while contenido.get("has_more", False):
            cursor = contenido.get("cursor")
            cont_uri = "https://api.dropboxapi.com/2/files/list_folder/continue"
            cont_data = json.dumps({"cursor": cursor})
            response = requests.post(cont_uri, headers=headers, data=cont_data)
            contenido = response.json()
            entries.extend(contenido.get("entries", []))
        msg_listbox = helper.update_listbox2(msg_listbox, self._path, {"entries": entries})
        self._files = msg_listbox

    def transfer_file(self, file_path, file_data):
        uri = 'https://content.dropboxapi.com/2/files/upload'
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
        requests.post(uri, headers=headers, data=file_data)

    def delete_file(self, file_path):
        uri = 'https://api.dropboxapi.com/2/files/delete_v2'
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"path": file_path})
        requests.post(uri, headers=headers, data=data)

    def create_folder(self, path):
        uri = 'https://api.dropboxapi.com/2/files/create_folder_v2'
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"path": path, "autorename": False})
        requests.post(uri, headers=headers, data=data)

    def rename_file(self, from_path, to_path):
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
        print("/rename_file Status:", response.status_code)
        print("Respuesta:", response.text)