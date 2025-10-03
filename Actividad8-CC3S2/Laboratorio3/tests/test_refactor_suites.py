import pytest
from unittest.mock import Mock
from src.shopping_cart import ShoppingCart


class TestPrecisionMonetaria:
    def test_suma_pequenas_cantidades(self):
        # Arrange
        cart = ShoppingCart()
        cart.add_item("x", 1, 0.05)
        cart.add_item("x", 1, 0.05)
        # Act
        total = cart.calculate_total()
        # Assert
        assert round(total, 2) == 0.10


class TestPasarelaPagoContratos:
    def test_pago_exitoso(self):
        # Arrange
        pg = Mock()
        cart = ShoppingCart(payment_gateway=pg)
        cart.add_item("x", 1,  10.0)
        pg.process_payment.return_value = True
        # Act
        total = cart.calculate_total()
        resultado = cart.process_payment(total)
        # Assert
        assert resultado is True
        pg.process_payment.assert_called_once_with(10.0)