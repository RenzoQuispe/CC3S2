import pytest
from unittest.mock import Mock
from src.shopping_cart import ShoppingCart


def test_pago_exitoso():
    # Arrange
    pg = Mock()
    cart = ShoppingCart(payment_gateway=pg)
    cart.add_item("x", 1, 10.0)
    pg.process_payment.return_value = True
    # Act
    total = cart.calculate_total()
    resultado = cart.process_payment(total)
    # Assert
    assert resultado is True
    pg.process_payment.assert_called_once_with(total)

def test_pago_timeout_sin_reintento_automatico():
    # Arrange
    pg = Mock()
    cart = ShoppingCart(payment_gateway=pg)
    cart.add_item("x", 1, 10.0)
    total = cart.calculate_total()
    pg.process_payment.side_effect = TimeoutError("timeout")
    # Act / Assert
    with pytest.raises(TimeoutError):
        cart.process_payment(total)
    # El SUT no debe reintentar automáticamente
    assert pg.process_payment.call_count == 1
    # reintento manual desde el test
    pg.process_payment.side_effect = None
    pg.process_payment.return_value = True
    assert pg.process_payment(total) is True  # reintento manual exitos

def test_pago_rechazo_definitivo():
    # Arrange
    pg = Mock()
    cart = ShoppingCart(payment_gateway=pg)
    cart.add_item("x", 1, 10.0)
    total = cart.calculate_total()
    pg.process_payment.return_value = False
    # Act
    resultado = cart.process_payment(total)
    # Assert
    assert resultado is False
    pg.process_payment.assert_called_once_with(total)