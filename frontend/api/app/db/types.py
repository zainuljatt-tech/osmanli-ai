from app.core.config import settings

def get_vector_type(dimensions: int = 1536):
    try:
        from sqlalchemy.dialects.postgresql import VECTOR
        return VECTOR(dimensions)
    except ImportError:
        from sqlalchemy import Text
        return Text


def get_uuid_type():
    if settings.USE_SQLITE:
        from sqlalchemy import String
        return String(36)
    from sqlalchemy.dialects.postgresql import UUID
    import uuid as _uuid
    return UUID(as_uuid=True)


def make_uuid():
    import uuid
    if settings.USE_SQLITE:
        return str(uuid.uuid4())
    return uuid.uuid4()
