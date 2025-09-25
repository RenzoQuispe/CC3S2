from flask import Flask, jsonify
import os
import sys
import json
import datetime

# 12-Factor: configuración vía variables de entorno (sin valores codificados)
PORT = int(os.environ.get("PORT", "8080"))
MESSAGE = os.environ.get("MESSAGE", "Hola")
RELEASE = os.environ.get("RELEASE", "v1")

app = Flask(__name__)

def log(event, **kwargs):
    entry = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "event": event,
        "port": PORT,
        "release": RELEASE,
        **kwargs
    }
    print(json.dumps(entry), file=sys.stdout, flush=True)

@app.route("/")
def root():
    log("http_request", method="GET", path="/", message=MESSAGE, status=200)
    return jsonify(
        status="ok",
        message=MESSAGE,
        release=RELEASE,
        port=PORT,
    )

if __name__ == "__main__":
    log("server_start", message=MESSAGE)
    # 12-Factor: vincular a un puerto; proceso único; sin estado
    app.run(host="127.0.0.1", port=PORT)
