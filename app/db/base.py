from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.models.user import User  # noqa: F401, E402
from app.models.organization import Organization  # noqa: F401, E402
from app.models.membership import Membership  # noqa: F401, E402
from app.models.item import Item  # noqa: F401, E402
from app.models.audit_log import AuditLog  # noqa: F401, E402
