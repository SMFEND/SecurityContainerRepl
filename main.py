import os
from flask import Flask, request, jsonify
import requests
import hashlib

app = Flask(__name__)

# Список доверенных токенов
TRUSTED_TOKENS = {"valid_token_1", "valid_token_2"}


@app.route("/update", methods=["POST"])
def handle_update_request():
    token = request.json.get("token")

    if token in TRUSTED_TOKENS:
        # Вызываем сервис обновления
        try:
            response, status_code = get_update_file_route()
            if status_code == 200:
                # Передаем файл в сервис проверки
                verify_response_status_code = verify_update(response)
                if verify_response_status_code == 200:
                    # Передаем файл в сервис бэкапа
                    backup_response_status_code = make_backup()
                    if backup_response_status_code == 200:
                        return jsonify({
                            "status":
                            "success",
                            "message":
                            "Update processed successfully."
                        }), 200
                    else:
                        return jsonify({
                            "status": "error",
                            "message": "Backup failed."
                        }), 500
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Verification failed."
                    }), 400
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to download update."
                }), 500
        except requests.exceptions.RequestException as e:
            return jsonify({
                "status": "error",
                "message": f"Service communication error: {str(e)}"
            }), 500
    else:
        return jsonify({"status": "denied", "message": "Invalid token."}), 403


def make_backup():
    return 200


def verify_update(file):
    with open(file, 'rb') as opened_file:  # Открываем файл в бинарном режиме
        file_data = opened_file.read() 
        sha256_hash = hashlib.sha256(file_data).hexdigest()
        if sha256_hash == os.getenv('EXPECTED_HASH'):
            return 200
        else:
            return 400


def get_update_file_route():
    return './update.zip', 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
