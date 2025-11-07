#!/usr/bin/env python3
"""
Punto de entrada que une todos los patrones para generar una configuración Terraform completamente local en formato JSON.

El archivo resultante puede aplicarse con:

    $ cd terraform
    $ terraform init
    $ terraform apply

No se requieren credenciales de nube, demonio de Docker, ni dependencias externas.
"""

import os
from iac_patterns.builder import InfrastructureBuilder
from iac_patterns.singleton import ConfigSingleton
from iac_patterns.factory import TimestampedNullResourceFactory

def crear_local_modules():
    """Crea los módulos locales requeridos por Terraform si no existen."""
    modules = {
        "network": 'resource "null_resource" "net_example" { triggers = { tipo = "red" } }',
        "app": 'resource "null_resource" "app_example" { triggers = { tipo = "aplicacion" } }'
    }

    for name, content in modules.items():
        path = os.path.join("terraform", "modules", name)
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, "main.tf")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Creado módulo local: {file_path}")

def main() -> None:
    # Inicializa una configuración global única para el entorno "local-dev"
    config = ConfigSingleton(env_name="desarrollo-local")
    config.set("proyecto", "patrones_iac_locales")

    # Construye la infraestructura usando el nombre de entorno desde la configuración global
    builder = InfrastructureBuilder(env_name=config.env_name)

    # Construye 8 recursos null ficticios para demostrar escalabilidad (se puede aumentar)
    builder.build_null_fleet(count=5)

    # Agregar un recurso creado por la TimestampedNullResourceFactory. Ejercicio 2.2
    formatted_resource = TimestampedNullResourceFactory.create(
        name="timestamped_recurso",
        fmt="%Y%m%d-%H%M%S"
    )
    builder._module.add(formatted_resource)

    # Agrega un recurso final personalizado con una nota descriptiva
    builder.add_custom_resource(
        name="finalizador",
        triggers={"nota": "Recurso compuesto generado dinámicamente en tiempo de ejecución"}
    )

    # Recurso con mutación avanzada. Ejercicio 2.3
    builder.build_welcome_resource()

    # Ejercicio 2.4: Submódulos con Composite
    crear_local_modules()
    builder._module.add({
        "module": {
            "network": {"source": "./modules/network"},
            "app": {"source": "./modules/app"}
        }
    })

    # Ejercicio 2.5: Crear grupo personalizado de recursos
    builder.build_group(name="webservers", size=3)
    builder.build_group(name="databases", size=2)

    # Exporta el resultado a un archivo Terraform JSON en el directorio especificado
    builder.export(path=os.path.join("terraform", "main.tf.json"))

# Ejecuta la función principal si el archivo se ejecuta directamente
if __name__ == "__main__":
    main()
