"""YouTube Shorts content generator package.

Exposes the public API so consumers can import directly from the package
root (``from youtube_shorts_generator import YouTubeShortsGenerator``) instead
of reaching into the inner module.

Version: follows the generator's ``__version__``.
"""

from .youtube_shorts_generator import (
    CONTENT_TEMPLATES,
    HOOK_TEMPLATES,
    NICHES,
    YouTubeShortsGenerator,
    main,
)

__version__ = "1.1.0"

__all__ = [
    "CONTENT_TEMPLATES",
    "HOOK_TEMPLATES",
    "NICHES",
    "YouTubeShortsGenerator",
    "main",
]
