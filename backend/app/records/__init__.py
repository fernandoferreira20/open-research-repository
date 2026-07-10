"""Records package

This package exposes the records Blueprint and related modules.
Importing this package should not cause side effects beyond importing
module definitions.
"""

from .routes import records_bp

__all__ = ["records_bp"]
