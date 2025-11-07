## Ejercicio 2.1: Extensión del Singleton

- Se agregó un método `reset()` a `singleton.py` (limpia settings pero mantiene created_at) y se creó un test el para dicho método.
- Probar test desde la carpeta `LaboratorioModificado`:

    ```sh
    python3 -m tests.test_singleton_reset
    ```
- Se agregó archivos `salida_terraform.txt` y `salida_test.txt` en la carpeta `Ejercicio2.1`

## Ejercicio 2.2: Variación de la Factory

- Se modificó `factory.py` y `generate_infra.py`
- Se agregó `test_timestamped_factory.py`.
- Al ejecutar `generate_infra.py`, además de los recursos generados por NullResourceFactory, también se crea un recurso adicional con la fábrica TimestampedNullResourceFactory, usando un formato de timestamp personalizado.
- Probar test desde la carpeta `LaboratorioModificado`:
    ```sh
    python3 -m tests.test_timestamped_factory
    ```
- Se agregó archivos `salida_terraform.txt` y `salida_test.txt` en la carpeta `Ejercicio2.2`

## Ejercicio 2.3: Mutaciones avanzadas con Prototype

- Se modificó `builder.py` y `generate_infra.py`
- Se agregó el método build_welcome_resource() dentro de la clase InfrastructureBuilder, que clona un prototipo de null_resource, usa un mutator para insertar el bloque local_file y añade el recurso mutado al módulo compuesto.
- Se integró el nuevo método en el flujo principal, para que se genere el recurso mutado junto con el resto.
- Se agregó archivos `salida_terraform.txt` en la carpeta `Ejercicio2.3`