import pytest
from src.shopping_cart import ShoppingCart

@pytest.mark.skip(reason="Contrato: precisión binaria no se corrige en esta versión")
def test_total_precision_decimal_skip():
    # Arrange
    cart = ShoppingCart()
    cart.add_item("x", 1, 0.1); cart.add_item("x", 2, 0.2)
    # Act / Assert
    assert cart.calculate_total() == 0.5