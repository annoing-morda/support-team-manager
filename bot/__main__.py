"""Entry point for the Support Team Manager Bot."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.session import close_engine
from bot.handlers import common

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting Support Team Manager Bot...")

    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register handlers
    dp.include_router(common.router)

    # Start polling
    try:
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
    finally:
        # Cleanup
        await bot.session.close()
        await close_engine()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
