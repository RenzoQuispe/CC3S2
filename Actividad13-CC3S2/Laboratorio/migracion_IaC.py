import os, json

LEGACY_DIR = "legacy"
OUT_DIR    = "environments/app_legacy"

# crear directorio de Terraform
os.makedirs(OUT_DIR, exist_ok=True)

# leer config.cfg
config = {}
with open(os.path.join(LEGACY_DIR, "config.cfg")) as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key] = value

# leer run.sh
with open(os.path.join(LEGACY_DIR, "run.sh")) as f:
    script_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# generar network.tf.json (variables)
network_tf = {
    "variable": {
        "port": {
            "type": "string",
            "default": config.get("PORT", "8080"),
            "description": "Puerto de la aplicación"
        }
    }
}

with open(os.path.join(OUT_DIR, "network.tf.json"), "w") as f:
    json.dump(network_tf, f, indent=4, sort_keys=True)

# generar main.tf.json (recurso)
main_tf = {
    "resource": {
        "null_resource": {
            "legacy_app": {
                "triggers": {
                    "port": "${var.port}"
                },
                "provisioner": [
                    {
                        "local-exec": {
                            "command": f"echo 'Arrancando ${{var.port}}'"
                        }
                    }
                ]
            }
        }
    }
}

with open(os.path.join(OUT_DIR, "main.tf.json"), "w") as f:
    json.dump(main_tf, f, indent=4, sort_keys=True)

print(f"Generado Terraform en {OUT_DIR}/")
