#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path

OUTPUTS_FILE = "network/network_outputs.json"

class NetworkModuleOutput:
    """Lee las salidas publicadas por el módulo 'network'."""
    def __init__(self, outputs_path=OUTPUTS_FILE):
        path = Path(outputs_path)
        if not path.exists():
            raise FileNotFoundError(
                f"No se encontró {path}. Ejecuta primero 'terraform apply' en network/"
            )
        data = json.loads(path.read_text())
        try:
            self.name = data["outputs"]["name"]["value"]
            self.cidr = data["outputs"]["cidr"]["value"]
        except (KeyError, TypeError) as exc:
            raise KeyError(f"Formato inesperado en {path}") from exc


class ServerFactoryModule:
    """Define un null_resource que simula un servidor ligado a la subred.
       Ahora incluye inyección adicional de:
       - nombre visible del servidor
       - etiquetas (tags)
    """
    def __init__(
        self,
        name,
        zone="local",
        outputs_path=OUTPUTS_FILE,
        server_display_name="Servidor de Prueba",
        tags=None
    ):
        if tags is None:
            tags = {
                "env": "dev",
                "owner": "automation",
            }

        self._name = name
        self._zone = zone
        self._server_display_name = server_display_name
        self._tags = tags
        self._network = NetworkModuleOutput(outputs_path)
        self.resources = self._build()

    def _build(self):
        return {
            "resource": {
                "null_resource": {
                    self._name: {
                        "triggers": {
                            "server_name": self._name,
                            "server_display_name": self._server_display_name,
                            "tags": json.dumps(self._tags),
                            "subnet_name": self._network.name,
                            "subnet_cidr": self._network.cidr,
                            "zone": self._zone
                        },
                        "provisioner": [{
                            "local-exec": {
                                "command": (
                                    f"echo 'Creando servidor {self._server_display_name} "
                                    f"({self._name}) en subred {self._network.name} "
                                    f"(CIDR {self._network.cidr}, zona {self._zone})'"
                                )
                            }
                        }]
                    }
                }
            }
        }


if __name__ == "__main__":
    Path("main.tf.json").write_text(
        json.dumps(
            ServerFactoryModule(
                "hello-world",
                server_display_name="Servidor Hello World",
                tags={"env": "prod", "owner": "Renzo"}
            ).resources,
            indent=4,
            sort_keys=True
        )
    )
    print("main.tf.json generado con parámetros inyectados.")
