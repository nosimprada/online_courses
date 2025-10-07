from typing import List

from utils.daos.ticket import TicketDAO
from utils.database import AsyncSessionLocal
from utils.enums.ticket import TicketStatus
from utils.schemas.ticket import TicketCreateSchemaDB, TicketReadSchemaDB


async def create_ticket(data: TicketCreateSchemaDB) -> TicketReadSchemaDB:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.create(session, data)


async def get_ticket_by_user_id(user_id: int) -> TicketReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.get_by_user_id(session, user_id)


async def get_open_tickets() -> List[TicketReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.get_open(session)


async def get_pending_tickets() -> List[TicketReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.get_pending(session)


async def get_closed_tickets() -> List[TicketReadSchemaDB]:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.get_closed(session)


async def open_ticket(ticket_id: int) -> TicketReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.update_status(session, ticket_id, TicketStatus.OPEN)


async def close_ticket(ticket_id: int) -> TicketReadSchemaDB | None:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.update_status(session, ticket_id, TicketStatus.CLOSED)


async def delete_ticket(ticket_id: int) -> None:
    async with AsyncSessionLocal() as session:
        return await TicketDAO.delete(session, ticket_id)
