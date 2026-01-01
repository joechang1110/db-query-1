"""Test script to verify app loading and routes."""
import sys
sys.path.insert(0, '.')

from app.main import app

print('✅ FastAPI app loaded successfully')
print('\n📋 Available API routes:')
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(route.methods) if route.methods else 'N/A'
        print(f'  {methods:15} {route.path}')
    elif hasattr(route, 'path'):
        print(f'  {"ROUTE":15} {route.path}')

print('\n✅ All imports successful!')
