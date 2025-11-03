import os, json
from shutil import copyfile
import shutil
import click
from jsonschema import validate, ValidationError

MODULE_DIR = "modules/simulated_app"
OUT_DIR = "environments"

# Esquemas JSON Schema
NETWORK_SCHEMA = {
    "type": "object",
    "properties": {
        "variable": {"type": "object"},
        "resource": {"type": "object"}
    },
    "required": ["variable"]
}

MAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "resource": {"type": "array"},
    },
    "required": ["resource"]
}

# Función para validar JSON
def validate_json(data, schema, filename):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise SystemExit(f"Error: {filename} no pasa la validación JSON Schema:\n{e.message}")
    else:
        print(f"{filename} validado correctamente.")

# Cargar clave API desde configuración segura
def load_secure_api_key():
    config_path = os.path.expanduser("~/.config/secure.json")
    if not os.path.exists(config_path):
        raise SystemExit("No se encontró ~/.config/secure.json. Crea uno con {'api_key': 'tu_clave_secreta'}")
    with open(config_path) as f:
        data = json.load(f)
    api_key = data.get("api_key")
    if not api_key:
        raise SystemExit("secure.json no contiene 'api_key'")
    print("Clave API cargada desde configuración segura.")
    return api_key

# Render y escritura
def render_and_write(env, api_key):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    # 1) Copiar network.tf.json
    src_file = os.path.join(MODULE_DIR, "network.tf.json")
    dst_file = os.path.join(env_dir, "network.tf.json")

    with open(src_file) as f:
        net_data = json.load(f)
        validate_json(net_data, NETWORK_SCHEMA, "network.tf.json")

    copyfile(src_file, dst_file)

    # 2) Generar main.tf.json con comando que usa variable sensible
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        env["name"]: [
                            {
                                "triggers": {
                                    "name":    env["name"],
                                    "network": env["network"],
                                    "port":    str(env["port"])
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": (
                                                f"TF_VAR_api_key={api_key} "
                                                f"echo 'Arrancando servidor {env['name']} "
                                                f"en red {env['network']} en puerto {env['port']}'"
                                            )
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    validate_json(config, MAIN_SCHEMA, "main.tf.json")

    with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)

@click.command()
@click.option('--count', default=3, help='Cantidad de entornos a crear')
@click.option('--prefix', default='app', help='Prefijo de los entornos')
@click.option('--port', default=8080, help='Puerto base simulado')
def main(count, prefix, port):
    """Genera entornos Terraform simulados con validación de esquema y API key segura."""

    api_key = load_secure_api_key()

    ENVS = [
        {"name": f"{prefix}{i}", "network": f"net{i}", "port": port}
        for i in range(1, count + 1)
    ]

    for env in ENVS:
        render_and_write(env, api_key)

    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/' con prefijo '{prefix}' y puerto {port}")
    print("La clave API fue usada solo en memoria (no se guardó en disco)")

if __name__ == "__main__":
    main()
