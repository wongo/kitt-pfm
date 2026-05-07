"""KITT PFM — Entry point."""
import asyncio
import logging
import sys
from pathlib import Path

from Kitt_pfm.config import TELEGRAM_BOT_TOKEN, DB_PATH, LOG_LEVEL
from Kitt_pfm.db.database import init_db
from Kitt_pfm.bot.app import create_app

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("kitt_pfm")


async def main():
    log.info(f"Initializing database at {DB_PATH}")
    await init_db(DB_PATH)
    log.info("Starting KITT PFM bot...")
    app = create_app(TELEGRAM_BOT_TOKEN)

    await app.initialize()
    await app.start()
    log.info("KITT PFM is online.")

    # Run polling in a separate task so we can wait for shutdown signal
    import signal
    stop_event = asyncio.Event()

    def signal_handler(sig, frame):
        stop_event.set()

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: stop_event.set())

    # Wait until signaled to stop
    try:
        await stop_event.wait()
    finally:
        log.info("Shutting down KITT PFM bot...")
        await app.stop()
        await app.shutdown()
        log.info("KITT PFM is offline.")


def main_sync():
    """Synchronous entry point for first-run DB init."""
    from Kitt_pfm.config import DB_PATH
    from Kitt_pfm.db.database import init_db_sync
    log.info(f"Initializing database (sync) at {DB_PATH}")
    init_db_sync(DB_PATH)
    log.info("Database initialized. Run 'python -m Kitt_pfm.main' to start the bot.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        main_sync()
    else:
        # Python 3.14 compatibility: avoid asyncio.run() which has
        # event loop lifecycle issues with python-telegram-bot
        import os
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
