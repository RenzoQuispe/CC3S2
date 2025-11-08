"""Patrón Adapter

Convierte recursos null_resource a otros formatos como mock_cloud_bucket.
Permite adaptar la interfaz de un recurso a otra esperada por diferentes proveedores.
"""

from typing import Dict, Any

class MockBucketAdapter:
    """
    Adaptador que transforma un null_resource en un mock_cloud_bucket simulado.
    Útil para demostrar cómo adaptar recursos entre diferentes proveedores cloud.
    """

    def __init__(self, null_block: Dict[str, Any]) -> None:
        """
        Inicializa el adaptador con un bloque null_resource.

        Args:
            null_block: Diccionario con estructura de null_resource Terraform.
        """
        self.null = null_block

    def to_bucket(self) -> Dict[str, Any]:
        """
        Mapea triggers de null_resource a parámetros de bucket simulado.
        
        Returns:
            Diccionario con estructura de mock_cloud_bucket compatible con Terraform.
        """
        # Extraer el nombre del recurso null
        null_resource_block = self.null["resource"][0]["null_resource"][0]
        name = list(null_resource_block.keys())[0]
        
        # Obtener los triggers del null_resource
        triggers = null_resource_block[name][0].get("triggers", {})
        
        # Mapear a estructura de mock_cloud_bucket
        return {
            "resource": [{
                "mock_cloud_bucket": [{
                    name: [{
                        "name": name,
                        **triggers
                    }]
                }]
            }]
        }