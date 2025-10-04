from aiogram import Router

from handlers.bot.admin import router as admin_router
from handlers.bot.help import router as help_router
from handlers.bot.start import router as start_router

routers: list[Router] = [start_router, admin_router, help_router]

__all__ = ['routers']
