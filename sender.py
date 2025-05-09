import requests

SERVER_URL = "https://dynamic-visually-barnacle.ngrok-free.app"

def send_command(cmd):
    r = requests.post(f"{SERVER_URL}/set_command", json={"command": cmd})
    if r.status_code == 200:
        print("Commande envoyée avec succès")
    else:
        print("Erreur lors de l'envoi de la commande")

if __name__ == "__main__":
    while True:
        cmd = input("Commande à envoyer (exit pour quitter): ")
        if cmd == "exit":
            break
        send_command(cmd)