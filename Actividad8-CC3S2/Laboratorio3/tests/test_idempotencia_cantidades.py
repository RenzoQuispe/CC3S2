from src.carrito import Carrito, ItemCarrito, Producto
from src.factories import ProductoFactory

def test_actualizacion_idempotente():
    # Arrange
    c = Carrito()
    producto = ProductoFactory(nombre="un_producto", precio=3.25)
    c.agregar_producto(producto,2)
    total1 = c.calcular_total()
    # Act
    for _ in range(5):
        c.actualizar_cantidad(producto, 2)
    total2 = c.calcular_total()
    # Assert
    assert total1 == total2
    assert sum(i.cantidad for i in c.items) == 2