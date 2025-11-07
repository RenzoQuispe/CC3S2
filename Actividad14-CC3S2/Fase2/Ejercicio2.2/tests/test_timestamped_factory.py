#!/usr/bin/env python3
import os
import json
from datetime import datetime
from iac_patterns.factory import TimestampedNullResourceFactory

def test_timestamped_factory():
    resource = TimestampedNullResourceFactory.create(
        name="test_timestamped_resource",
        fmt='%Y%m%d'
    )
    
    null_resource = resource["resource"][0]["null_resource"][0]
    resource_name = list(null_resource.keys())[0]
    triggers = null_resource[resource_name][0]["triggers"]
    
    timestamp = triggers["timestamp"]
    assert len(timestamp) == 8
    assert timestamp.isdigit()
    
    today = datetime.utcnow().strftime('%Y%m%d')
    assert timestamp == today
    
    print("Test pasado")
    print(f"  - Timestamp: {timestamp}")

if __name__ == "__main__":
    test_timestamped_factory()