"""WhatsApp delivery bot for the YouTube Shorts generator.

Exposes the public classes from the package root.
"""

from .whatsapp_bot import WhatsAppClient, YouTubeShortsWhatsAppBot, cli

__version__ = "1.1.0"

__all__ = ["WhatsAppClient", "YouTubeShortsWhatsAppBot", "cli"]
