import os, json
from shutil import copyfile
import shutil
import click

MODULE_DIR = "modules/simulated_app"
OUT_DIR = "environments"

def render_and_write(env):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)

    # 1) Copia la definición de variables (network.tf.json)
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )

    # 2) Genera main.tf.json con el puerto incluido
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
                                                f"echo 'Arrancando servidor "
                                                f"{env['name']} en red {env['network']} en puerto {env['port']}'"
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

    with open(os.path.join(env_dir, "main.tf.json"), "w") as fp:
        json.dump(config, fp, sort_keys=True, indent=4)

@click.command()
@click.option('--count', default=3, help='Cantidad de entornos a crear')
@click.option('--prefix', default='app', help='Prefijo de los entornos')
@click.option('--port', default=8080, help='Puerto base simulado')
def main(count, prefix, port):
    """Genera entornos Terraform simulados."""

    ENVS = [
        {"name": f"{prefix}{i}", "network": f"net{i}", "port": port}
        for i in range(1, count + 1)
    ]

    for env in ENVS:
        render_and_write(env)

    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/' con prefijo '{prefix}' y puerto {port}")

if __name__ == "__main__":
    main()
