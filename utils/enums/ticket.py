import enum


class TicketStatus(enum.Enum):
    OPEN = "OPEN"  # РЕШАЕТСЯ В ДАННЫЙ МОМЕНТ
    RESOLVED = "RESOLVED"  # УЖЕ РЕШЕН И ЗАКРЫЛСЯ
    CLOSED = "CLOSED"  # ЕЩЕ НЕ ПРИНЯЛИ
