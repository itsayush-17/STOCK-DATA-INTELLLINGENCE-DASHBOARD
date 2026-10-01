"""
Analytics package for Smart Investment & Portfolio Analytics platform.
"""

try:
    from backend.analytics.engine import run_full_analysis
    from backend.analytics.seed import DEFAULT_MARKET_SNAPSHOT, DEFAULT_USER_PROFILE
except ImportError:
    from .engine import run_full_analysis
    from .seed import DEFAULT_MARKET_SNAPSHOT, DEFAULT_USER_PROFILE

__all__ = ["run_full_analysis", "DEFAULT_MARKET_SNAPSHOT", "DEFAULT_USER_PROFILE"]
