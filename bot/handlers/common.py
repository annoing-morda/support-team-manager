"""Common handlers for basic bot commands."""

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import settings

logger = logging.getLogger(__name__)

# Create router for common handlers
router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Handle /start command.
    
    Greets the user and provides basic information about the bot.
    """
    user = message.from_user
    if user is None:
        return

    logger.info(f"User {user.id} ({user.username}) started the bot")

    welcome_text = (
        f"👋 Привет, <b>{user.full_name}</b>!\n\n"
        "Я — <b>Support Admin Bot</b>, помощник для управления дежурствами "
        "команды технической поддержки.\n\n"
        "Используй команду /help, чтобы узнать, что я умею."
    )

    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Handle /help command.
    
    Shows list of available commands based on user role.
    """
    user = message.from_user
    if user is None:
        return

    logger.info(f"User {user.id} ({user.username}) requested help")

    # Check if user is admin
    is_admin = user.id in settings.admin_ids_list

    # Common commands for all users
    help_text = (
        "<b>📋 Доступные команды:</b>\n\n"
        "<b>Основные:</b>\n"
        "/start — Начать работу с ботом\n"
        "/help — Показать это сообщение\n"
        "/duty — Показать текущего дежурного\n"
        "/myduties — Мои предстоящие дежурства\n"
    )

    # Admin-only commands
    if is_admin:
        help_text += (
            "\n<b>Административные:</b>\n"
            "/employees — Список сотрудников\n"
            "/addemployee @username — Добавить сотрудника\n"
            "/setduty YYYY-MM-DD @username — Назначить дежурство\n"
            "/removeduty YYYY-MM-DD — Снять дежурство\n"
        )
    else:
        help_text += (
            "\n<i>ℹ️ Для доступа к административным командам "
            "обратитесь к администратору бота.</i>"
        )

    await message.answer(help_text)
