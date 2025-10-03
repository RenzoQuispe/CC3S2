import pytest
from unittest.mock import Mock
from src.shopping_cart import ShoppingCart

@pytest.mark.smoke
def test_smoke_agregar_y_total():
    cart = ShoppingCart()
    cart.add_item("x", 1, 1.0)
    assert cart.calculate_total() == 1.0

@pytest.mark.smoke
def test_smoke_pago_exitoso():
    pg = Mock()
    cart = ShoppingCart(payment_gateway=pg)
    cart.add_item("x", 1, 10.0)
    pg.process_payment.return_value = True
    total = cart.calculate_total()
    assert cart.process_payment(total) is True

@pytest.mark.smoke
def test_smoke_pago_rechazado():
    pg = Mock()
    cart = ShoppingCart(payment_gateway=pg)
    cart.add_item("x", 1, 10.0)
    pg.process_payment.return_value = False
    total = cart.calculate_total()
    assert cart.process_payment(total) is False

@pytest.mark.regression
def test_regression_descuento_redondeo():
    cart = ShoppingCart()
    cart.add_item("x", 1, 10.0)
    cart.apply_discount(15)
    assert round(cart.calculate_total(), 2) == 8.50