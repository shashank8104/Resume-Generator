"""
Vercel serverless function entry point for Resume Intelligence API
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.main import app

# Export for Vercel
handler = app
