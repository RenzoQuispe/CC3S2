from src.carrito import Carrito, ItemCarrito, Producto
from src.factories import ProductoFactory

def test_invariante_agregar_remover_y_actualizar():
    # Arrange
    c = Carrito()
    producto = ProductoFactory(nombre="x", precio=5.0)
    c.agregar_producto(producto=producto, cantidad=3)
    t1 = c.calcular_total()
    # Act
    c.remover_producto(producto=producto, cantidad=3)
    t2 = c.calcular_total()
    c.agregar_producto(producto=producto, cantidad=3)
    c.actualizar_cantidad(producto=producto, nueva_cantidad=0)
    t3 = c.calcular_total()
    # Assert
    assert c.calcular_total() == 0.0
    assert sum(i.cantidad for i in c.items) == 0
    assert t1 == 15.0
    assert t2 == 0
    assert t3 == 0