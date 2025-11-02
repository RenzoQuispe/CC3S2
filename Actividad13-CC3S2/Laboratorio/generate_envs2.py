import os, json
from shutil import copyfile

ENVS = [
    {"name": "env1", "network": "net1"},
    {"name": "env2", "network": "net2"},
    {"name": "env3", "network": None}
]

MODULE_DIR = "modules/simulated_app"
OUT_DIR = "environments"

# definir dependencias
NETWORK_DEPENDENCIES = {
    "env3": "env2"  # env3 depende de la red de env2
}

def render_and_write(env, envs_dict):
    env_dir = os.path.join(OUT_DIR, env["name"])
    os.makedirs(env_dir, exist_ok=True)
    # copiar network.tf.json base
    copyfile(
        os.path.join(MODULE_DIR, "network.tf.json"),
        os.path.join(env_dir, "network.tf.json")
    )
    # determinaromos red
    if env["name"] in NETWORK_DEPENDENCIES:
        dep_name = NETWORK_DEPENDENCIES[env["name"]]
        env["network"] = f"{envs_dict[dep_name]['network']}-peered"
    # generar main.tf.json
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        env["name"]: [
                            {
                                "triggers": {
                                    "name": env["name"],
                                    "network": env["network"]
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": (
                                                f"echo 'Arrancando servidor "
                                                f"{env['name']} en red {env['network']}'"
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

if __name__ == "__main__":

    envs_dict = {env["name"]: env for env in ENVS}

    for env in ENVS:
        render_and_write(env, envs_dict)

    print(f"Generados {len(ENVS)} entornos en '{OUT_DIR}/'")
