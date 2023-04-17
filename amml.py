"""
    The main script of the loader.
"""

import os
import subprocess
import http.server
import socketserver
# import re
from typing import Union, Optional, TypedDict

import minecraft_launcher_lib
from minecraft_launcher_lib import microsoft_account

mc_directory = os.path.join(os.getcwd(), 'mcdir')

client_id = "9d4eb936-02b6-445e-a7fd-51ccce4ab536"
redirect_url = "http://127.0.0.1:8000/"
version = "1.16.5"

minecraft_launcher_lib.install.install_minecraft_version(version, mc_directory)

login_url = microsoft_account.get_login_url(
    client_id, redirect_url)

print(login_url)


class CodeContainer(TypedDict):
    code: Optional[str]


def wait_for_code(port: int):
    container = CodeContainer(code=None)

    class RedirectHandler(http.server.BaseHTTPRequestHandler):

        def do_GET(self):
            # global wait_for_code.code
            # code_match = re.search(r"(?<=code=)[\w.-]+", self.path)
            # print(self.path)
            # print(code_match)
            # print(code_match.group())
            container["code"] = microsoft_account.get_auth_code_from_url(
                self.path)

            self.send_response(200)
            self.send_header("Content-Length", "text/html")
            self.end_headers()

#            self.wfile.write(b'<script>window.close()</script>')

    with socketserver.TCPServer(("", port), RedirectHandler) as httpd:
        print("Waiting for socket event.")
        httpd.handle_request()

    return container["code"]



code = wait_for_code(8000)
print(f"code: {code}")

# login

login_data = microsoft_account.complete_login(client_id, None, redirect_url, code, None)

options: minecraft_launcher_lib.types.MinecraftOptions = {
    "username": login_data["name"],
    "uuid": login_data["id"],
    "token": login_data["access_token"]
}

# launch

def launch_mc(version: str, dir: Union[str, os.PathLike],
              options: minecraft_launcher_lib.utils.MinecraftOptions):
    launch_command = minecraft_launcher_lib.command.get_minecraft_command(
        version, dir, options)

    subprocess.Popen(launch_command)

launch_mc(version, mc_directory, options)
