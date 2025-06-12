# Import all the models, so that TimestampedBase has them before being imported by Alembic

from db.base_class import TimestampedBase as Base  # noqa: F401
from db.tables.golf_assistant import GolfSession, GolfTranscript  # noqa: F401
