import pytest
from src.carrito import Carrito
from src.factories import ProductoFactory

@pytest.mark.parametrize(
    "precio,cantidad,descuento,esperado",
    [
        (10.00, 1, 0, 10.00),
        (10.00, 1, 1, 9.90),
        (10.01, 1, 33.33, 6.67),
        (100.00, 1, 50, 50.00),
        (1.00, 1, 99.99, 0.00),
        (50.00, 1, 100, 0.00),
    ],
)
def test_descuento_total(precio, cantidad, descuento, esperado):
    # arrange
    carrito = Carrito()
    producto = ProductoFactory(nombre="p", precio=precio)
    carrito.agregar_producto(producto, cantidad)
    # act
    total_con_descuento = carrito.aplicar_descuento(descuento)
    # assert
    assert round(total_con_descuento, 2) == pytest.approx(esperado, abs=0.01)