# Reporte

## Análisis

Durante el desarrollo de las pruebas unitarias en los distintas partes del laboratorio se aplicaron técnicas y herramientas relacionadas a testing con Python. Las aserciones fueron la base de las pruebas, permitiendo verificar el comportamiento esperado de las funciones, los fixtures facilitaron la preparación y limpieza del entorno de prueba asegurando que los datos y el estado de la base de datos fueran consistentes antes y después de cada ejecucion y el uso de coverage permitió medir la cobertura del código, se aseguro tener una alta cobertura antes de terminar cada parte del laboratorio. 

Las factories y fakes se emplearon para generar datos de prueba sin depender de recursos externos y el mocking se uso para simular dependencias externas(API de IMDB en nuestro caso). Incluso se aplicó un mini-ciclo TDD donde primero escribimos pruebas que fallaban, luego hicimos el codigo que las hace pasar y finalmente un mejora del diseño implementado, este ciclo de Red-Green-Refactor lo repetimos para el resto de funcionalidades. En conjunto, estas prácticas se integran para fomentar un desarrollo completo, robusto, mantenible y con informacion acerca de la fiabilidad de nuestro código.

## Resultados

### Resumen

| Carpeta     | Tests Totales | Tests Aprobados | Cobertura | Líneas sin cubrir | Archivos sin cobertura                              |
| ---------------------- | ------------- | --------------- | ---------------- | ----------------- | --------------------------------------------------------------- |
| aserciones_pruebas | 8             | 8             | 100%         | 0                 | —                                                               |
| pruebas_pytest     | 11            | 11            | 100%         | 0                 | —                                                               |
| pruebas_fixtures   | 2             | 2             | 69%          | 13                | `models/account.py` (líneas 25, 29, 33-34, 44-47, 51-53, 71-72) |
| coverage_pruebas   | 13            | 13            | 97%          | 1                 | `models/__init__.py` (línea 12)                                 |
| factories_fakes    | 8             | 8             | 100%         | 0                 | —                                                               |
| mocking_objetos    | 6             | 6             | 88%          | 2                 | `models/imdb.py` (líneas 36, 46)                                |



- Total de pruebas ejecutadas: 48

- Total de pruebas exitosas: 48 / 48 (100%)

- Líneas totales sin cubrir: 16

### `aserciones_pruebas`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/aserciones_pruebas$ pytest
========================================================= test session starts =========================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/aserciones_pruebas
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 8 items                                                                                                                     

test_stack.py::TestStack::test_is_empty PASSED                                                                                  [ 12%]
test_stack.py::TestStack::test_peek PASSED                                                                                      [ 25%]
test_stack.py::TestStack::test_pop PASSED                                                                                       [ 37%]
test_stack.py::TestStack::test_push PASSED                                                                                      [ 50%]
test_stack.py::test_is_empty PASSED                                                                                             [ 62%]
test_stack.py::test_peek PASSED                                                                                                 [ 75%]
test_stack.py::test_pop PASSED                                                                                                  [ 87%]
test_stack.py::test_push PASSED                                                                                                 [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name       Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------
stack.py      12      0      0      0   100%
------------------------------------------------------
TOTAL         12      0      0      0   100%


========================================================== 8 passed in 0.29s ==========================================================
```

### `pruebas_pytest`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/pruebas_pytest$ pytest
========================================================= test session starts =========================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/pruebas_pytest
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 11 items                                                                                                                    

test_triangle.py::TestAreaOfTriangle::test_float_values PASSED                                                                  [  9%]
test_triangle.py::TestAreaOfTriangle::test_integer_values PASSED                                                                [ 18%]
test_triangle.py::TestAreaOfTriangle::test_negative_base PASSED                                                                 [ 27%]
test_triangle.py::TestAreaOfTriangle::test_negative_height PASSED                                                               [ 36%]
test_triangle.py::TestAreaOfTriangle::test_negative_values PASSED                                                               [ 45%]
test_triangle.py::TestAreaOfTriangle::test_with_boolean PASSED                                                                  [ 54%]
test_triangle.py::TestAreaOfTriangle::test_with_nulls PASSED                                                                    [ 63%]
test_triangle.py::TestAreaOfTriangle::test_with_string PASSED                                                                   [ 72%]
test_triangle.py::TestAreaOfTriangle::test_zero_base PASSED                                                                     [ 81%]
test_triangle.py::TestAreaOfTriangle::test_zero_height PASSED                                                                   [ 90%]
test_triangle.py::TestAreaOfTriangle::test_zero_values PASSED                                                                   [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name               Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------
test_triangle.py      30      0      0      0   100%
triangle.py           10      0      8      0   100%
--------------------------------------------------------------
TOTAL                 40      0      8      0   100%


========================================================= 11 passed in 0.38s ==========================================================
```

### `pruebas_fixtures`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/pruebas_fixtures$ pytest
======================================================== test session starts =========================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/pruebas_fixtures
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 2 items                                                                                                                    

tests/test_account.py::TestAccountModel::test_create_an_account PASSED                                                         [ 50%]
tests/test_account.py::TestAccountModel::test_create_all_accounts PASSED                                                       [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
models/__init__.py       6      0      0      0   100%
models/account.py       40     13      8      0    65%   25, 29, 33-34, 44-47, 51-53, 71-72
----------------------------------------------------------------
TOTAL                   46     13      8      0    69%


========================================================= 2 passed in 1.15s ==========================================================
```

### `coverage_pruebas `

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/coverage_pruebas$ pytest
======================================================== test session starts =========================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/coverage_pruebas
configfile: setup.cfg
testpaths: tests
plugins: cov-5.0.0, Faker-37.11.0
collected 13 items                                                                                                                   

tests/test_account.py::TestAccountModel::test_create_an_account PASSED                                                         [  7%]
tests/test_account.py::TestAccountModel::test_create_all_accounts PASSED                                                       [ 15%]
tests/test_account.py::TestAccountModel::test_to_dict PASSED                                                                   [ 23%]
tests/test_account.py::TestAccountModel::test_from_dict PASSED                                                                 [ 30%]
tests/test_account.py::TestAccountModel::test_update_account_success PASSED                                                    [ 38%]
tests/test_account.py::TestAccountModel::test_update_account_no_id_error PASSED                                                [ 46%]
tests/test_account.py::TestAccountModel::test_delete_account PASSED                                                            [ 53%]
tests/test_account.py::TestAccountModel::test_find_account_exists PASSED                                                       [ 61%]
tests/test_account.py::TestAccountModel::test_find_account_not_exists PASSED                                                   [ 69%]
tests/test_account.py::TestAccountModel::test_repr_account PASSED                                                              [ 76%]
tests/test_account.py::TestAccountModel::test_validate_info_valida PASSED                                                      [ 84%]
tests/test_account.py::TestAccountModel::test_validate_nombre_vacio PASSED                                                     [ 92%]
tests/test_account.py::TestAccountModel::test_validate_invalid_email PASSED                                                    [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
models/__init__.py       9      1      2      1    82%   12
models/account.py       53      0     14      0   100%
----------------------------------------------------------------
TOTAL                   62      1     16      1    97%
Coverage HTML written to dir htmlcov


========================================================= 13 passed in 1.37s =========================================================
```

### `factories_fakes`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/factories_fakes$ pytest
====================================================== test session starts ======================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/factories_fakes
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 8 items                                                                                                               

tests/test_account.py::TestAccountModel::test_crear_todas_las_cuentas PASSED                                              [ 12%]
tests/test_account.py::TestAccountModel::test_crear_una_cuenta PASSED                                                     [ 25%]
tests/test_account.py::TestAccountModel::test_repr PASSED                                                                 [ 37%]
tests/test_account.py::TestAccountModel::test_to_dict PASSED                                                              [ 50%]
tests/test_account.py::TestAccountModel::test_from_dict PASSED                                                            [ 62%]
tests/test_account.py::TestAccountModel::test_actualizar_una_cuenta PASSED                                                [ 75%]
tests/test_account.py::TestAccountModel::test_id_invalido_al_actualizar PASSED                                            [ 87%]
tests/test_account.py::TestAccountModel::test_eliminar_una_cuenta PASSED                                                  [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
models/__init__.py       6      0      0      0   100%
models/account.py       43      0      8      0   100%
----------------------------------------------------------------
TOTAL                   49      0      8      0   100%


======================================================= 8 passed in 1.43s =======================================================
```

### `mocking_objetos`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/mocking_objetos$ pytest
====================================================== test session starts ======================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/mocking_objetos
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 6 items                                                                                                               

tests/test_imdb.py::TestIMDbDatabase::test_search_titles_success PASSED                                                   [ 16%]
tests/test_imdb.py::TestIMDbDatabase::test_search_titles_failure PASSED                                                   [ 33%]
tests/test_imdb.py::TestIMDbDatabase::test_movie_reviews_success PASSED                                                   [ 50%]
tests/test_imdb.py::TestIMDbDatabase::test_movie_ratings_success PASSED                                                   [ 66%]
tests/test_imdb.py::TestIMDbDatabase::test_search_by_title_failed PASSED                                                  [ 83%]
tests/test_imdb.py::TestIMDbDatabase::test_movie_ratings_good PASSED                                                      [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
models/__init__.py       2      0      0      0   100%
models/imdb.py          25      2      6      2    87%   36, 46
----------------------------------------------------------------
TOTAL                   27      2      6      2    88%


======================================================= 6 passed in 0.61s =======================================================
```

### `practica_tdd`

```
(venv) jquispe@pc1-quispe:~/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/practica_tdd$ pytest
====================================================== test session starts ======================================================
platform linux -- Python 3.13.5, pytest-8.3.3, pluggy-1.6.0 -- /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/jquispe/Escritorio/cursos/CC3S2/Actividad9-CC3S2/soluciones/practica_tdd
configfile: setup.cfg
plugins: cov-5.0.0, Faker-37.11.0
collected 9 items                                                                                                               

test_counter.py::test_create_a_counter PASSED                                                                             [ 11%]
test_counter.py::test_duplicate_counter PASSED                                                                            [ 22%]
test_counter.py::test_update_counter PASSED                                                                               [ 33%]
test_counter.py::test_read_counter PASSED                                                                                 [ 44%]
test_counter.py::test_delete_counter PASSED                                                                               [ 55%]
test_counter.py::test_increment_counter PASSED                                                                            [ 66%]
test_counter.py::test_set_counter PASSED                                                                                  [ 77%]
test_counter.py::test_list_counters PASSED                                                                                [ 88%]
test_counter.py::test_reset_counter PASSED                                                                                [100%]

---------- coverage: platform linux, python 3.13.5-final-0 -----------
Name         Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------
counter.py      49      2     24      2    95%   42, 74
--------------------------------------------------------
TOTAL           49      2     24      2    95%


======================================================= 9 passed in 0.82s =======================================================
```