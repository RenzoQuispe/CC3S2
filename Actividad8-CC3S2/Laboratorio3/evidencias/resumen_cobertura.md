### Reporte Cobertura

Se alcanzó un 96% de cobertura total, con la mayoría de los módulos en src/ superando el 90%, los archivos carrito.py y shopping_cart.py tienen la mayoría de líneas sin cubrir, principalmente en rutas de error. En cuanto a los tests, la gran mayoría tienen cobertura completa, a excepcion de test_mre_precision.py (44%) y test_rgr_precision_verde.py (57%), que quedaron con secciones no ejecutadas ya que esos tests estan marcados como skip.

En la ejecución se registran 39 tests pasados, con 2 skip, 2 xfail (fallas esperadas`) y 2 xpass (tests marcados como fallidos que en realidad pasaron). La cobertura nos da un nivel alto, tenemos 96% de cobertura total y ademas tenemos claro las razones de ese 4% faltante.

Tras ejecutar `make cov` tenemos:

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad8-CC3S2/Laboratorio3$ make cov
========================================== test session starts ===========================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad8-CC3S2/Laboratorio3
configfile: pytest.ini
testpaths: tests
plugins: cov-5.0.0, Faker-37.8.0
collected 45 items                                                                                       

tests/test_carrito.py .........                                                                    [ 20%]
tests/test_descuentos_parametrizados.py ......                                                     [ 33%]
tests/test_estabilidad_semillas.py .                                                               [ 35%]
tests/test_idempotencia_cantidades.py .                                                            [ 37%]
tests/test_invariantes_inventario.py .                                                             [ 40%]
tests/test_markers.py ....                                                                         [ 48%]
tests/test_mensajes_error.py x                                                                     [ 51%]
tests/test_mre_precision.py s                                                                      [ 53%]
tests/test_pasarela_pago_contratos.py ...                                                          [ 60%]
tests/test_precios_frontera.py ....XX                                                              [ 73%]
tests/test_redondeo_acumulado.py ..                                                                [ 77%]
tests/test_refactor_suites.py ..                                                                   [ 82%]
tests/test_rgr_precision_rojo.py x                                                                 [ 84%]
tests/test_rgr_precision_verde.py s                                                                [ 86%]
tests/test_shopping_cart.py ......                                                                 [100%]

================================================ XPASSES =================================================

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                               0      0   100%
src/carrito.py                               55      6    89%   9, 21, 50, 52, 60, 91
src/factories.py                              7      0   100%
src/shopping_cart.py                         29      2    93%   27, 31
tests/__init__.py                             0      0   100%
tests/test_carrito.py                        71      0   100%
tests/test_descuentos_parametrizados.py      10      0   100%
tests/test_estabilidad_semillas.py           21      0   100%
tests/test_idempotencia_cantidades.py        12      0   100%
tests/test_invariantes_inventario.py         17      0   100%
tests/test_markers.py                        30      0   100%
tests/test_mensajes_error.py                  8      0   100%
tests/test_mre_precision.py                   9      5    44%   7-13
tests/test_pasarela_pago_contratos.py        33      0   100%
tests/test_precios_frontera.py               16      0   100%
tests/test_redondeo_acumulado.py             20      0   100%
tests/test_refactor_suites.py                20      0   100%
tests/test_rgr_precision_rojo.py              7      0   100%
tests/test_rgr_precision_verde.py             7      3    57%   7-10
tests/test_shopping_cart.py                  47      0   100%
-----------------------------------------------------------------------
TOTAL                                       419     16    96%

======================================== short test summary info =========================================
SKIPPED [1] tests/test_mre_precision.py:4: Contrato: Reemplazo en vez de acumulación no se corrige en esta versión
SKIPPED [1] tests/test_rgr_precision_verde.py:4: Contrato: precisión binaria no se corrige en esta versión
XFAIL tests/test_mensajes_error.py::test_mensaje_error_contiene_contexto - Producto no encontrado en el carrito
XFAIL tests/test_rgr_precision_rojo.py::test_total_precision_decimal - Float binario puede introducir error en dinero
XPASS tests/test_precios_frontera.py::test_precios_invalidos[0.0] - Contrato no definido para precio=0 o negativo
XPASS tests/test_precios_frontera.py::test_precios_invalidos[-1.0] - Contrato no definido para precio=0 o negativo
========================== 39 passed, 2 skipped, 2 xfailed, 2 xpassed in 0.89s ===========================
```