#!/usr/bin/env python3
"""
Validación del método reset() del ConfigSingleton

Verifica que:
- El método reset() limpia el diccionario settings
- El método reset() mantiene el created_at original
"""

from iac_patterns.singleton import ConfigSingleton

def test_reset():
    """Prueba el método reset() del Singleton"""
    # Crear instancia y guardar el timestamp original
    c1 = ConfigSingleton("dev")
    created = c1.created_at
    
    # Agregar configuración
    c1.settings["x"] = 1
    
    # Ejecutar reset
    c1.reset()
    
    # Validaciones
    assert c1.settings == {}, f"Error: settings debería estar vacío, pero contiene {c1.settings}"
    assert c1.created_at == created, f"Error: created_at cambió de {created} a {c1.created_at}"
    
    print("Test reset() pasado exitosamente")
    print(f"  - settings limpiado: {c1.settings}")
    print(f"  - created_at preservado: {c1.created_at}")

if __name__ == "__main__":
    test_reset()