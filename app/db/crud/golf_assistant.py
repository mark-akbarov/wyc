from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.base import BaseCrud
from db.tables.golf_assistant import GolfSession, GolfTranscript
from schemas.golf_assistant import (
    InGolfSessionSchema,
    UpdateGolfSessionSchema,
    OutGolfSessionSchema,
    PaginatedGolfSessionSchema,
    InGolfTranscriptSchema,
    UpdateGolfTranscriptSchema,
    OutGolfTranscriptSchema,
    PaginatedGolfTranscriptSchema,
)


class GolfSessionCrud(
    BaseCrud[
        InGolfSessionSchema,
        UpdateGolfSessionSchema,
        OutGolfSessionSchema,
        PaginatedGolfSessionSchema,
        GolfSession,
    ]
):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    @property
    def _table(self):
        return GolfSession

    @property
    def _out_schema(self):
        return OutGolfSessionSchema

    @property
    def default_ordering(self):
        return desc(self._table.created_at)

    @property
    def _paginated_schema(self):
        return PaginatedGolfSessionSchema

    async def get_by_session_id(self, session_id: str, active_only=True):
        """
        Get a session by its session_id (not the primary key)
        """
        result = await self._db_session.execute(
            self.apply_active_statement(
                select(*self.out_schema_columns)
                .select_from(self._table)
                .where(self._table.session_id == session_id),
                active_only,
            )
        )
        entry = result.first()
        if not entry:
            return None
        return self._out_schema.model_validate(entry)


class GolfTranscriptCrud(
    BaseCrud[
        InGolfTranscriptSchema,
        UpdateGolfTranscriptSchema,
        OutGolfTranscriptSchema,
        PaginatedGolfTranscriptSchema,
        GolfTranscript,
    ]
):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)

    @property
    def _table(self):
        return GolfTranscript

    @property
    def _out_schema(self):
        return OutGolfTranscriptSchema

    @property
    def default_ordering(self):
        return desc(self._table.created_at)

    @property
    def _paginated_schema(self):
        return PaginatedGolfTranscriptSchema

    async def get_by_session_id(self, session_id: int, limit=10, active_only=True):
        """
        Get transcripts for a specific session
        """
        result = await self._db_session.execute(
            self.apply_active_statement(
                select(*self.out_schema_columns)
                .select_from(self._table)
                .where(self._table.session_id == session_id),
                active_only,
            )
            .order_by(desc(self._table.created_at))
            .limit(limit)
        )
        entries = result.all()
        return [self._out_schema.model_validate(entry) for entry in entries]