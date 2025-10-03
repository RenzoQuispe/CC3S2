import pytest
from src.carrito import Carrito

@pytest.mark.xfail(reason="Producto no encontrado en el carrito")
def test_mensaje_error_contiene_contexto():
    c = Carrito()
    with pytest.raises(ValueError) as e:
        c.actualizar_cantidad("inexistente", 1)
    assert "inexistente" in str(e.value)