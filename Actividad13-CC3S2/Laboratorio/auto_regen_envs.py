#!/usr/bin/env python3
import os
import subprocess
import time
import hashlib
import json

MODULE_DIR = "modules/simulated_app"
ENV_DIR = "environments"
GENERATE_CMD = ["python3", "generate_envs.py", "--count", "3", "--prefix", "app", "--port", "3000"]
CACHE_FILE = ".modules_hash_cache.json"

def hash_directory(path):   # Devuelve un hash SHA256 de todos los archivos dentro del directorio.
    h = hashlib.sha256()
    for root, _, files in os.walk(path):
        for f in sorted(files):
            fp = os.path.join(root, f)
            with open(fp, "rb") as file:
                h.update(file.read())
    return h.hexdigest()

def load_cached_hash():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f).get("hash", "")
    return ""

def save_cached_hash(h):
    with open(CACHE_FILE, "w") as f:
        json.dump({"hash": h}, f)

def regen_envs():
    print("Cambios detectados en modules/simulated_app — Regenerando entornos...")
    subprocess.run(GENERATE_CMD, check=True)
    print("Entornos regenerados correctamente.\n")

def main():
    current_hash = hash_directory(MODULE_DIR)
    cached_hash = load_cached_hash()

    if current_hash != cached_hash:
        regen_envs()
        save_cached_hash(current_hash)
    else:
        print("No hay cambios en modules/simulated_app. Nada que regenerar.")

if __name__ == "__main__":
    main()
