import random
from faker import Faker
from src.carrito import Carrito
from src.factories import ProductoFactory

def test_estabilidad_semillas(capsys):
    faker = Faker()

    # primera ejecucion
    random.seed(123)
    faker.seed_instance(123)
    carrito = Carrito()
    producto = ProductoFactory(nombre="p1", precio=7.0)
    carrito.agregar_producto(producto=producto)
    print(carrito.calcular_total())
    out1 = capsys.readouterr().out

    # Segunda ejecucion (mismas semillas)
    random.seed(123)
    faker.seed_instance(123)
    carrito = Carrito()
    producto = ProductoFactory(nombre="p2", precio=7.0)
    carrito.agregar_producto(producto=producto)
    print(carrito.calcular_total())
    out2 = capsys.readouterr().out

    assert out1 == out2