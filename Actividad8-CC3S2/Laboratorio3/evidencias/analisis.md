### Ejercicio A1: Descuentos parametrizados

| Entrada (precio, cantidad y descuento) | Total esperado |
| ------------------------------------- | -------------- |
| 10.00, 1, 0                           | 10.00          |
| 10.00, 1, 1                           | 9.90           |
| 10.01, 1, 33.33                       | 6.67           |
| 100.00, 1, 50                         | 50.00          |
| 1.00, 1, 99.99                        | 0.00           |
| 50.00, 1, 100                         | 0.00           |

### Ejercicio A4: Redondeos acumulados vs. final

| Redondeo en la suma por item | Redondeo al final | Diferencia |
| --------------------| ------------| ------------------------|
| 3.0000000000000004  | 3.0         |   0.0000000000000004    |
|  7.552 |    7.555      |   -0.003    |

### Ejercicios B1-B2-B3

- Rojo

    El test `test_total_precision_decimal()` falla, y usamos `xfail` para no detener el flujo de pruebas y tener claro la razon por la cual falla, el test queda como mejora pendiente del sistema.

- Verde

    En el test `test_total_precision_decimal_skip()` con `skip` saltamos esta prueba, ya que por el momento no es importante si el test pasa o falla ya que no es un objetivo inmediato del equipo tener listo esta funcionalidad.

- Refactor

    Con un mock se simula el comportamiento real de payment_gateway sin necesidad de conectarse a un servicio externo, gracias al mock se pudo controlar la respuesta de process_payment y verificar que el carrito llamara a la pasarela con el monto correcto.

### Ejercicio C1: Contratos de pasarela de pago con mock

| Evento                                | Expectativa                                                                 |
|---------------------------------------|------------------------------------------------------------------------------|
| Pago exitoso                          | `process_payment` devuelve `True` y se confirma la llamada con el monto.     |
| Pago con timeout                      | Se lanza `TimeoutError` y no hay reintentos automáticos.                     |
| Reintento manual tras timeout         | Si el mock se reconfigura, el pago puede completarse correctamente.          |
| Pago rechazado por pasarela           | `process_payment` devuelve `False` y no se intenta nuevamente.               |
| Pasarela no proporcionada             | Se lanza `ValueError` al intentar procesar el pago sin `payment_gateway`.    |

### Ejercicio C3: Umbral de cobertura

Se configuró un umbral de 90% como quality gate. La ejecución alcanzó un 90.11%, cumpliendo el mínimo. Mejoras según `term-missing`:

- `src/carrito.py`: líneas 9, 21, 50, 52, 60, 68, 91 (ej. ramas no ejecutadas o validaciones no probadas).
- `src/shopping_cart.py`: líneas 27, 31 (manejo de excepción en `process_payment`).

### Ejercicio C4: MREs para defectos

Tenemos reemplazo en vez de acumulación en `tests/test_mre_precision.py`. Explicación:

- Agregamos dos veces el mismo producto `un-producto` con precios distintos (0.1 y 0.2).
- El total debería sumar ambos (`0.1 + 0.2 = 0.3`).
- El carrito devuelve `0.2` ,solo considera el último precio.
