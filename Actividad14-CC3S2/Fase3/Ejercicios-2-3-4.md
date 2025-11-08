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

- Se agregó `tests/test_patterns.py`. Contiene tests de Singleton (identidad, estado compartido, reset), tests de Prototype (clones independientes, deep copy), tests de Factory (recursos válidos, triggers), tests de Composite (agregación, módulos), tests de Builder (interfaz fluida, flota) ytests de Adapter (conversión, preservación de nombres)
- Para probar los tests se necesita crear un entorno virtual e instalar pytest.
- Salida de la ejecución de los tests
    ```
    (venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad14-CC3S2/Fase3/LaboratorioModificado$ pytest tests/test_patterns.py -v
    ==================================================== test session starts ====================================================
    platform linux -- Python 3.13.5, pytest-8.4.2, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad14-CC3S2/Fase3/LaboratorioModificado/venv/bin/python3
    cachedir: .pytest_cache
    rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad14-CC3S2/Fase3/LaboratorioModificado
    collected 14 items                                                                                                          

    tests/test_patterns.py::TestSingletonPattern::test_singleton_meta PASSED                                              [  7%]
    tests/test_patterns.py::TestSingletonPattern::test_singleton_shared_state PASSED                                      [ 14%]
    tests/test_patterns.py::TestSingletonPattern::test_singleton_reset PASSED                                             [ 21%]
    tests/test_patterns.py::TestPrototypePattern::test_prototype_clone_independent PASSED                                 [ 28%]
    tests/test_patterns.py::TestPrototypePattern::test_prototype_deep_copy PASSED                                         [ 35%]
    tests/test_patterns.py::TestFactoryPattern::test_factory_creates_valid_resource PASSED                                [ 42%]
    tests/test_patterns.py::TestFactoryPattern::test_factory_default_triggers PASSED                                      [ 50%]
    tests/test_patterns.py::TestFactoryPattern::test_factory_custom_triggers PASSED                                       [ 57%]
    tests/test_patterns.py::TestCompositePattern::test_composite_aggregates_resources PASSED                              [ 64%]
    tests/test_patterns.py::TestCompositePattern::test_composite_handles_modules PASSED                                   [ 71%]
    tests/test_patterns.py::TestBuilderPattern::test_builder_fluent_interface PASSED                                      [ 78%]
    tests/test_patterns.py::TestBuilderPattern::test_builder_creates_fleet PASSED                                         [ 85%]
    tests/test_patterns.py::TestAdapterPattern::test_adapter_converts_null_to_bucket PASSED                               [ 92%]
    tests/test_patterns.py::TestAdapterPattern::test_adapter_preserves_name PASSED                                        [100%]

    ===================================================== warnings summary ======================================================
    tests/test_patterns.py: 13 warnings
    /home/jquispe/Escritorio/cursos/CC3S2/Actividad14-CC3S2/Fase3/LaboratorioModificado/iac_patterns/factory.py:34: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
        triggers.setdefault("timestamp", datetime.utcnow().isoformat())

    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    ============================================== 14 passed, 13 warnings in 0.06s ==============================================
    ```
## 3.4 Escalabilidad de JSON

- Se agregó el script `scripts/measure_scalability.py` que mide tamaños y tiempos para 15 vs 150 recursos.

- Probar el script con `python3 -m scripts.medir_escalabilidad` dessde la carpeta `LaboratorioModificado`

    ```
    jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad14-CC3S2/Fase3/LaboratorioModificado$ python3 -m scripts.medir_escalabilidad 
    MEDICIÓN DE ESCALABILIDAD DE TERRAFORM JSON
    Generando infraestructura con 15 recursos...
    [Builder] Terraform JSON escrito en: terraform_escalabilidad/main_15.tf.json

    Métricas de escalabilidad:
    - Recursos generados: 15
    - Tamaño del archivo: 7.26 KB (7,431 bytes)
    - Líneas de código: 229
    - Tiempo de construcción: 0.0005s
    - Tiempo de exportación: 0.0009s
    - Tiempo total: 0.0015s
    - Archivo generado: terraform_escalabilidad/main_15.tf.json
    Generando infraestructura con 150 recursos...
    [Builder] Terraform JSON escrito en: terraform_escalabilidad/main_150.tf.json

    Métricas de escalabilidad:
    - Recursos generados: 150
    - Tamaño del archivo: 72.61 KB (74,356 bytes)
    - Líneas de código: 2,254
    - Tiempo de construcción: 0.0046s
    - Tiempo de exportación: 0.0089s
    - Tiempo total: 0.0135s
    - Archivo generado: terraform_escalabilidad/main_150.tf.json
    COMPARACIÓN Y ANÁLISIS

    De 15 a 150 recursos:
    - Incremento de tamaño: 10.01x (7.26 KB -> 72.61 KB)
    - Incremento de tiempo: 9.00x (0.0015s -> 0.0135s)
    - Bytes por recurso (promedio):
        - 15 recursos: 495 bytes/recurso
        - 150 recursos: 496 bytes/recurso

    Reporte completo guardado en: terraform_escalabilidad/escalabilidad_report.json
    ```

- Tras ejecutar el script se crear los siguientes archivos:
    ```
    terraform_escalabilidad/
    ├── escalabilidad_report.json
    ├── main_150.tf.json
    └── main_15.tf.json
    ```

### Escalabilidad de JSON en Terraform

Generar archivos JSON grandes en Terraform puede afectar directamente los pipelines de CI/CD, a medida que aumenta la cantidad de recursos, el tiempo que tarda Terraform en parsear, validar y construir dependencias también crece. Por ejemplo, pasar de 15 a 150 recursos puede multiplicar por diez el tamaño del archivo y alargar notablemente los tiempos de ejecución de terraform plan. Además, los archivos JSON muy grandes pueden acercarse a los límites de GitHub y aumentar el tamaño histórico del repositorio. También pueden consumir mucha memoria en los runners de CI/CD, provocando errores en entornos con recursos limitados, tambien los diffs generados por cambios automáticos en estos archivos suelen ser enormes y un poco mas dificiles de revisar.

Para evitar estos problemas, se recomienda dividir la infraestructura en módulos independientes (por ejemplo, network, compute, storage), de modo que cada uno tenga su propio estado y pueda aplicarse por separado, tambien es buena práctica usar workspaces o backends distintos por entorno o región, así como cambiar de JSON a HCL, ya que este formato es más compacto y soporta expresiones dinámicas (for_each, count).

Cuando la infraestructura supera los 50 o 100 recursos por módulo, conviene adoptar una estructura modular, usar HCL nativo y apoyarse en herramientas de orquestación. Con esto se mejora la escalabilidad, el rendimiento y la mantenibilidad del pipeline de CI/CD.