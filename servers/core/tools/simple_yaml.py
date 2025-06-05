"""
Simple YAML parser fallback for when PyYAML is not available.
This provides basic functionality for simple YAML structures.
"""

import json
import re


class SimpleYAMLLoader:
    """A very basic YAML parser for simple structures."""
    
    @staticmethod
    def safe_load(content):
        """Parse simple YAML content."""
        if isinstance(content, str):
            # Very basic YAML parsing - convert common patterns to JSON-like structure
            lines = content.strip().split('\n')
            return SimpleYAMLLoader._parse_lines(lines)
        return content
    
    @staticmethod
    def _parse_lines(lines):
        """Parse YAML lines into a Python structure."""
        result = {}
        current_key = None
        current_list = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle key-value pairs
            if ':' in line and not line.startswith('-'):
                if current_list is not None:
                    result[current_key] = current_list
                    current_list = None
                    
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value:
                    # Simple value
                    result[key] = SimpleYAMLLoader._parse_value(value)
                else:
                    # Prepare for nested structure or list
                    current_key = key
                    result[key] = {}
                    
            # Handle list items
            elif line.startswith('-'):
                value = line[1:].strip()
                if current_list is None:
                    current_list = []
                current_list.append(SimpleYAMLLoader._parse_value(value))
                
        # Finalize any pending list
        if current_list is not None and current_key is not None:
            result[current_key] = current_list
            
        return result
    
    @staticmethod
    def _parse_value(value):
        """Parse a value, handling common types."""
        value = value.strip()
        
        # Remove quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
            
        # Handle numbers
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
            
        # Handle booleans
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False
            
        return value


# Create yaml module interface
def safe_load(stream):
    """Safe load function compatible with PyYAML."""
    if hasattr(stream, 'read'):
        content = stream.read()
    else:
        content = stream
    return SimpleYAMLLoader.safe_load(content)
