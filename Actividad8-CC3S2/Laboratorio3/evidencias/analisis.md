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

