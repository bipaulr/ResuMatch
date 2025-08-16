import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Now import the actual main application from backend
from backend.main import api

# The api object is now available for uvicorn to import as main:api
