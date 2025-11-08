#!/usr/bin/env python3
"""
Script para medir la escalabilidad de archivos Terraform JSON. Genera archivos con diferentes cantidades de recursos y mide su tamaño.
"""

import os
import json
import time
from iac_patterns.builder import InfrastructureBuilder
from iac_patterns.singleton import ConfigSingleton

def measure_file_size(path: str) -> int:
    """Retorna el tamaño del archivo en bytes"""
    return os.path.getsize(path)

def format_size(bytes_size: int) -> str:
    """Formatea bytes a una representación legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def generate_and_measure(fleet_size: int, output_dir: str = "terraform_escalabilidad"):
    """
    Genera un archivo Terraform con N recursos y mide métricas
        - fleet_size: Cantidad de recursos a generar
        - output_dir: Directorio de salida
        - return: Diccionario con métricas medidas
    """

    print(f"Generando infraestructura con {fleet_size} recursos...")
    
    # limpiar singleton para medición limpia
    config = ConfigSingleton(env_name=f"scale-test-{fleet_size}")
    config.reset()
    config.set("fleet_size", fleet_size)
    
    # medir tiempo de construcción
    start_build = time.time()
    builder = InfrastructureBuilder(env_name=config.env_name)
    builder.build_null_fleet(count=fleet_size)
    build_time = time.time() - start_build
    
    # medir tiempo de exportación
    output_path = os.path.join(output_dir, f"main_{fleet_size}.tf.json")
    os.makedirs(output_dir, exist_ok=True)
    
    start_export = time.time()
    builder.export(path=output_path)
    export_time = time.time() - start_export
    
    # medir tamaño del archivo
    file_size = measure_file_size(output_path)
    
    # contar líneas
    with open(output_path, 'r') as f:
        line_count = sum(1 for _ in f)
    
    # leer y analizar estructura
    with open(output_path, 'r') as f:
        content = json.load(f)
        resource_count = len(content.get("resource", []))
    
    metrics = {
        "fleet_size": fleet_size,
        "file_size_bytes": file_size,
        "file_size_formatted": format_size(file_size),
        "line_count": line_count,
        "resource_count": resource_count,
        "build_time_seconds": round(build_time, 4),
        "export_time_seconds": round(export_time, 4),
        "total_time_seconds": round(build_time + export_time, 4),
        "output_path": output_path
    }
    
    return metrics

def print_metrics(metrics: dict):
    """Imprime métricas de forma legible"""
    print(f"\nMétricas de escalabilidad:")
    print(f" - Recursos generados: {metrics['resource_count']}")
    print(f" - Tamaño del archivo: {metrics['file_size_formatted']} ({metrics['file_size_bytes']:,} bytes)")
    print(f" - Líneas de código: {metrics['line_count']:,}")
    print(f" - Tiempo de construcción: {metrics['build_time_seconds']}s")
    print(f" - Tiempo de exportación: {metrics['export_time_seconds']}s")
    print(f" - Tiempo total: {metrics['total_time_seconds']}s")
    print(f" - Archivo generado: {metrics['output_path']}")

def main():
    """Ejecuta las mediciones de escalabilidad"""
    print("MEDICIÓN DE ESCALABILIDAD DE TERRAFORM JSON")
    
    # tamaños a probar
    sizes_to_test = [15, 150]
    
    all_metrics = []
    
    for size in sizes_to_test:
        metrics = generate_and_measure(size)
        print_metrics(metrics)
        all_metrics.append(metrics)
    
    # comparación
    print("COMPARACIÓN Y ANÁLISIS")
    if len(all_metrics) >= 2:
        small = all_metrics[0]
        large = all_metrics[1]
        
        size_ratio = large["file_size_bytes"] / small["file_size_bytes"]
        time_ratio = large["total_time_seconds"] / small["total_time_seconds"]
        
        print(f"\nDe {small['fleet_size']} a {large['fleet_size']} recursos:")
        print(f" - Incremento de tamaño: {size_ratio:.2f}x ({small['file_size_formatted']} -> {large['file_size_formatted']})")
        print(f" - Incremento de tiempo: {time_ratio:.2f}x ({small['total_time_seconds']}s -> {large['total_time_seconds']}s)")
        print(f" - Bytes por recurso (promedio):")
        print(f"    - {small['fleet_size']} recursos: {small['file_size_bytes'] / small['resource_count']:.0f} bytes/recurso")
        print(f"    - {large['fleet_size']} recursos: {large['file_size_bytes'] / large['resource_count']:.0f} bytes/recurso")
    
    # guardar resultados
    results_path = "terraform_escalabilidad/escalabilidad_report.json"
    with open(results_path, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"\nReporte completo guardado en: {results_path}")

if __name__ == "__main__":
    main()