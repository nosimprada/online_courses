from aiogram import Router

from handlers.bot.start import router as start_router

routers: list[Router] = [start_router]

__all__ = ['routers']
