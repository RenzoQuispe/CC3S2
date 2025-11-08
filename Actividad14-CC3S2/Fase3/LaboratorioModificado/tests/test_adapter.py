#!/usr/bin/env python3
"""
Test de integración del patrón Adapter

Genera recursos adaptados a mock_cloud_bucket y valida con Terraform
"""

import os
import json
from iac_patterns.builder import InfrastructureBuilder
from iac_patterns.singleton import ConfigSingleton

def test_adapter_integration():
    """Prueba el patrón Adapter integrando mock_cloud_bucket"""
    
    # Configuración
    config = ConfigSingleton(env_name="test-adapter")
    config.set("proyecto", "test_adapter_pattern")
    
    # Crear builder
    builder = InfrastructureBuilder(env_name=config.env_name)
    
    # Agregar recursos null tradicionales
    builder.build_null_fleet(count=3)
    
    # Agregar recursos adaptados a bucket (usando Adapter pattern)
    builder.add_adapted_bucket(
        name="data_bucket",
        triggers={
            "region": "us-east-1",
            "versioning": "enabled",
            "encryption": "AES256"
        }
    )
    
    builder.add_adapted_bucket(
        name="logs_bucket",
        triggers={
            "region": "eu-west-1",
            "lifecycle_days": "30",
            "storage_class": "STANDARD_IA"
        }
    )
    
    # exportar
    output_dir = "terraform_adapter_test"
    output_path = os.path.join(output_dir, "adapter.tf.json")
    builder.export(path=output_path)
    
    # leer y validar
    with open(output_path, "r") as f:
        result = json.load(f)
    
    # validaciones
    assert "resource" in result, "Debe contener 'resource'"
    
    # buscar recursos mock_cloud_bucket
    buckets_found = []
    for resource_block in result["resource"]:
        if "mock_cloud_bucket" in resource_block:
            bucket_list = resource_block["mock_cloud_bucket"]
            for bucket in bucket_list:
                bucket_name = list(bucket.keys())[0]
                buckets_found.append(bucket_name)
    
    assert "data_bucket" in buckets_found, "Debe contener data_bucket"
    assert "logs_bucket" in buckets_found, "Debe contener logs_bucket"
    
    print("Test Adapter pasado exitosamente")
    print(f"\nRecursos generados:")
    print(f"  - Buckets adaptados: {buckets_found}")
    print(f"  - Total de recursos: {len(result['resource'])}")
    
    print(f"\nContenido del JSON exportado:")
    print(json.dumps(result, indent=2)[:500] + "...")
    
    print(f"\nArchivo generado: {output_path}")
    print(f"\nNOTA: mock_cloud_bucket es un tipo de recurso simulado.")
    print("Para Terraform real, se necesita un provider que lo soporte.")

if __name__ == "__main__":
    test_adapter_integration()