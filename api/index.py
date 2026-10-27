"""
Vercel serverless function entry point for Resume Intelligence API
"""
import sys
import os
from pathlib import Path

# Set working directory to project root so relative paths work (e.g. configs/config.yaml)
project_root = Path(__file__).parent.parent
os.chdir(str(project_root))

# Add project root to path for imports
sys.path.insert(0, str(project_root))

from src.api.main import app

# Export for Vercel
handler = app
