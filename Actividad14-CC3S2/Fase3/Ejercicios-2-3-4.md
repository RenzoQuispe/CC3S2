## 3.2 Patrones avanzados: Adapter


- Se agregaron `iac_patterns/adapter.py` y `tests/test_adapter.py`
- Se modificó `iac_patterns/builder.py` (se añadió método `add_adapted_bucket()`)
- Se implemento el patrón Adapter para integrar recursos simulados tipo mock_cloud_bucket dentro del flujo del InfrastructureBuilder. La clase MockBucketAdapter en `adapter.py` toma un bloque null_resource y lo transforma en un recurso con estructura de bucket, mapeando sus triggers como atributos del mismo. En `builder.py` se añadio el método add_adapted_bucket, que genera un null_resource, lo adapta usando el MockBucketAdapter y lo agrega al módulo principal. `test_adapter.py` tiene una prueba de integración que crea varios recursos adaptados (como data_bucket y logs_bucket), exporta el archivo adapter.tf.json y valida que los buckets simulados se generen correctamente.

- Probar test desde la carpeta `LaboratorioModificado`:

    ```sh
    python3 -m tests.test_adapter
    ```
- `mock_cloud_bucket` es un recurso simulado para demostrar el patrón Adapter. El provider no existe en el registro de Terraform, por lo que terraform init falla. El objetivo es mostrar la transformación de estructura.

## 3.3 Tests automatizados con pytest

## 3.4 Escalabilidad de JSON