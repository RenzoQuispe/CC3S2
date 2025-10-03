import pytest
from src.carrito import Carrito, ItemCarrito, Producto
from src.factories import ProductoFactory

@pytest.mark.parametrize("precio", [0.01, 0.005, 0.0049, 9999999.99])
def test_precios_frontera(precio):
    # Arrange
    carrito = Carrito()
    producto = ProductoFactory(nombre="un_producto", precio=precio)
    carrito.agregar_producto(producto, 1)
    # Act
    total = carrito.calcular_total()
    # Assert
    assert total >= 0

@pytest.mark.xfail(reason="Contrato no definido para precio=0 o negativo")
@pytest.mark.parametrize("precio_invalido", [0.0, -1.0])
def test_precios_invalidos(precio_invalido):
    carrito = Carrito()
    producto = ProductoFactory(nombre="un-producto", precio=precio_invalido)
    carrito.agregar_producto(producto, 1)