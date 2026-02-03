"""Database dependency re-export for backwards compatibility.

The actual database implementation is in app.db.mongodb.
This module provides a convenient import path from app.core.
"""

from app.db.mongodb import MongoDB, get_database

__all__ = ["MongoDB", "get_database"]
