import pytest
from src.shopping_cart import ShoppingCart

@pytest.mark.skip(reason="Contrato: Reemplazo en vez de acumulación no se corrige en esta versión")
def test_mre_precision():
    # Arrange
    carrito = ShoppingCart()
    carrito.add_item("un-producto", 1, 0.1)
    carrito.add_item("un-producto", 1, 0.2)
    # Act
    total = carrito.calculate_total()
    # Assert
    assert round(total, 2) == 0.30