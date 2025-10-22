from aiogram import Router

from handlers.bot.admin import router as admin_router
from handlers.bot.course import router as course_router
from handlers.bot.help import router as help_router
from handlers.bot.renewal import router as renewal_router
from handlers.bot.start import router as start_router

routers: list[Router] = [start_router, admin_router, help_router, course_router, renewal_router]

__all__ = ['routers']
