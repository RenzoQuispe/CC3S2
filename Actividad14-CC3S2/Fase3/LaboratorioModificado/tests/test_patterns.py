#!/usr/bin/env python3

import pytest
from iac_patterns.singleton import ConfigSingleton, SingletonMeta
from iac_patterns.factory import NullResourceFactory
from iac_patterns.prototype import ResourcePrototype
from iac_patterns.composite import CompositeModule
from iac_patterns.builder import InfrastructureBuilder
from iac_patterns.adapter import MockBucketAdapter

class TestSingletonPattern:
    """Tests para el patrón Singleton"""
    
    def test_singleton_meta(self):
        """Verifica que dos instancias sean la misma (identidad)"""
        a = ConfigSingleton("X")
        b = ConfigSingleton("Y")
        assert a is b, "Las instancias deben ser idénticas (mismo objeto en memoria)"
    
    def test_singleton_shared_state(self):
        """Verifica que el estado sea compartido entre instancias"""
        c1 = ConfigSingleton("env1")
        c1.set("key1", "value1")
        
        c2 = ConfigSingleton("env2")
        assert c2.get("key1") == "value1", "El estado debe ser compartido"
    
    def test_singleton_reset(self):
        """Verifica que reset() limpie settings pero mantenga created_at"""
        config = ConfigSingleton("test")
        original_created_at = config.created_at
        
        config.set("test_key", "test_value")
        config.reset()
        
        assert config.settings == {}, "Settings debe estar vacío después de reset"
        assert config.created_at == original_created_at, "created_at debe mantenerse"

class TestPrototypePattern:
    """Tests para el patrón Prototype"""
    
    def test_prototype_clone_independent(self):
        """Verifica que los clones sean independientes del original"""
        proto = ResourcePrototype(NullResourceFactory.create("app"))
        c1 = proto.clone(lambda b: b.__setitem__("f1", 1))
        c2 = proto.clone(lambda b: b.__setitem__("b1", 2))
        
        assert "f1" not in c2.data, "c2 no debe tener modificaciones de c1"
        assert "b1" not in c1.data, "c1 no debe tener modificaciones de c2"
    
    def test_prototype_deep_copy(self):
        """Verifica que el clonado sea profundo (deep copy)"""
        original = NullResourceFactory.create("test")
        proto = ResourcePrototype(original)
        
        clone = proto.clone()
        
        # Modificar el clon no debe afectar al original
        clone_triggers = clone.data["resource"][0]["null_resource"][0]["test"][0]["triggers"]
        clone_triggers["new_key"] = "new_value"
        
        original_triggers = original["resource"][0]["null_resource"][0]["test"][0]["triggers"]
        assert "new_key" not in original_triggers, "El original no debe verse afectado"

class TestFactoryPattern:
    """Tests para el patrón Factory"""
    
    def test_factory_creates_valid_resource(self):
        """Verifica que Factory cree recursos válidos"""
        resource = NullResourceFactory.create("test_resource")
        
        assert "resource" in resource
        assert len(resource["resource"]) > 0
        assert "null_resource" in resource["resource"][0]
    
    def test_factory_default_triggers(self):
        """Verifica que Factory agregue triggers por defecto"""
        resource = NullResourceFactory.create("test")
        triggers = resource["resource"][0]["null_resource"][0]["test"][0]["triggers"]
        
        assert "factory_uuid" in triggers, "Debe tener factory_uuid"
        assert "timestamp" in triggers, "Debe tener timestamp"
    
    def test_factory_custom_triggers(self):
        """Verifica que Factory acepte triggers personalizados"""
        custom_triggers = {"env": "production", "region": "us-east-1"}
        resource = NullResourceFactory.create("test", custom_triggers)
        triggers = resource["resource"][0]["null_resource"][0]["test"][0]["triggers"]
        
        assert triggers["env"] == "production"
        assert triggers["region"] == "us-east-1"

class TestCompositePattern:
    """Tests para el patrón Composite"""
    
    def test_composite_aggregates_resources(self):
        """Verifica que Composite agregue múltiples recursos"""
        composite = CompositeModule()
        
        composite.add(NullResourceFactory.create("res1"))
        composite.add(NullResourceFactory.create("res2"))
        composite.add(NullResourceFactory.create("res3"))
        
        result = composite.export()
        assert len(result["resource"]) == 3, "Debe tener 3 recursos"
    
    def test_composite_handles_modules(self):
        """Verifica que Composite maneje submódulos"""
        composite = CompositeModule()
        
        module_block = {
            "module": {
                "network": {
                    "source": "./modules/network"
                }
            }
        }
        
        composite.add(module_block)
        result = composite.export()
        
        assert "module" in result
        assert "network" in result["module"]

class TestBuilderPattern:
    """Tests para el patrón Builder"""
    
    def test_builder_fluent_interface(self):
        """Verifica que Builder soporte interfaz fluida"""
        builder = InfrastructureBuilder("test")
        
        # Debe poder encadenar llamadas
        result = builder.build_null_fleet(2).add_custom_resource("test", {})
        
        assert result is builder, "Debe retornar self para encadenamiento"
    
    def test_builder_creates_fleet(self):
        """Verifica que Builder cree flotas de recursos"""
        import tempfile
        import json
        import os
        
        builder = InfrastructureBuilder("test")
        builder.build_null_fleet(count=5)
        
        # Exportar a archivo temporal
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.tf.json")
            builder.export(output_path)
            
            # Leer y validar
            with open(output_path, "r") as f:
                result = json.load(f)
            
            assert len(result["resource"]) >= 5, "Debe tener al menos 5 recursos"

class TestAdapterPattern:
    """Tests para el patrón Adapter"""
    
    def test_adapter_converts_null_to_bucket(self):
        """Verifica que Adapter convierta null_resource a mock_cloud_bucket"""
        null_resource = NullResourceFactory.create("test_bucket", {
            "region": "us-west-2",
            "encryption": "enabled"
        })
        
        adapter = MockBucketAdapter(null_resource)
        bucket = adapter.to_bucket()
        
        assert "resource" in bucket
        assert "mock_cloud_bucket" in bucket["resource"][0]
        
        # Verificar que los triggers se mapearon correctamente
        bucket_block = bucket["resource"][0]["mock_cloud_bucket"][0]["test_bucket"][0]
        assert bucket_block["region"] == "us-west-2"
        assert bucket_block["encryption"] == "enabled"
    
    def test_adapter_preserves_name(self):
        """Verifica que Adapter preserve el nombre del recurso"""
        null_resource = NullResourceFactory.create("my_bucket")
        adapter = MockBucketAdapter(null_resource)
        bucket = adapter.to_bucket()
        
        bucket_names = list(bucket["resource"][0]["mock_cloud_bucket"][0].keys())
        assert "my_bucket" in bucket_names, "El nombre debe preservarse"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])