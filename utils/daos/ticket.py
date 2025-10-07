from datetime import datetime
from typing import List, Sequence

from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.enums.ticket import TicketStatus
from utils.models.ticket import Ticket
from utils.schemas.ticket import TicketCreateSchemaDB, TicketReadSchemaDB


class TicketDAO:
    @staticmethod
    async def create(session: AsyncSession, data: TicketCreateSchemaDB) -> TicketReadSchemaDB:
        ticket = Ticket(
            user_id=data.user_id,
            topic=data.topic,
            text=data.text,
            attachments=data.attachments
        )

        session.add(ticket)

        await session.commit()
        await session.refresh(ticket)

        return TicketReadSchemaDB.model_validate(ticket)

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: int) -> TicketReadSchemaDB | None:
        result = await session.execute(select(Ticket).where(Ticket.user_id == user_id))
        ticket = result.scalars().all()

        return TicketReadSchemaDB.model_validate(ticket) if ticket else None

    @staticmethod
    async def get_open(session: AsyncSession) -> List[TicketReadSchemaDB]:
        result = await session.execute(select(Ticket).where(Ticket.status == TicketStatus.OPEN))

        tickets: Sequence[Ticket] = result.scalars().all()
        return [TicketReadSchemaDB.model_validate(ticket) for ticket in tickets]

    @staticmethod
    async def get_pending(session: AsyncSession) -> List[TicketReadSchemaDB]:
        result = await session.execute(select(Ticket).where(Ticket.status == TicketStatus.PENDING))

        tickets: Sequence[Ticket] = result.scalars().all()
        return [TicketReadSchemaDB.model_validate(ticket) for ticket in tickets]

    @staticmethod
    async def get_closed(session: AsyncSession) -> List[TicketReadSchemaDB]:
        result = await session.execute(select(Ticket).where(Ticket.status == TicketStatus.CLOSED))

        tickets: Sequence[Ticket] = result.scalars().all()
        return [TicketReadSchemaDB.model_validate(ticket) for ticket in tickets]

    @staticmethod
    async def update_status(session: AsyncSession, ticket_id: int, status: TicketStatus) -> TicketReadSchemaDB | None:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()

        if ticket:
            ticket.status = status

            if status == TicketStatus.CLOSED:
                ticket.resolved_at = datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None)

            await session.commit()
            await session.refresh(ticket)

            return TicketReadSchemaDB.model_validate(ticket)

        return None

    @staticmethod
    async def delete(session: AsyncSession, ticket_id: int) -> None:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()

        if ticket:
            await session.delete(ticket)
            await session.commit()

        return None
