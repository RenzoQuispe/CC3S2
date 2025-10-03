from src.carrito import Carrito, ItemCarrito, Producto
from src.factories import ProductoFactory

def test_redondeo_acumulado_vs_final1():
    # Arrange
    c = Carrito()
    p1 = ProductoFactory(nombre="producto1", precio=0.3333)
    p2 = ProductoFactory(nombre="producto2", precio=0.6667)
    c.agregar_producto(p1, 3)
    c.agregar_producto(p2, 3)
    # Act
    total = c.calcular_total()
    suma_por_item = sum(round(i.producto.precio, 3)*i.cantidad for i in c.items)
    # Assert
    assert round(total, 3) != suma_por_item

def test_redondeo_acumulado_vs_final2():
    # Arrange
    c = Carrito()
    p1 = ProductoFactory(nombre="producto1", precio=0.5555)
    p2 = ProductoFactory(nombre="producto2", precio=1.3333)
    c.agregar_producto(p1, 4)
    c.agregar_producto(p2, 4)
    # Act
    total = c.calcular_total()
    suma_por_item = sum(round(i.producto.precio, 3)*i.cantidad for i in c.items)
    # Assert
    assert round(total, 3) != suma_por_item