from threading import Lock

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from app.agent.schemas import Turn
from app.config import settings


class MemoryBase(DeclarativeBase):
    pass


class SessionTurn(MemoryBase):
    __tablename__ = "session_turns"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(index=True)
    role: Mapped[str]
    content: Mapped[str]


# ponytail: in-memory SQLite on one shared connection, lost on restart; use the file DB if sessions must survive
_engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
MemoryBase.metadata.create_all(_engine)
_lock = Lock()


def get_history(session_id: str) -> list[Turn]:
    query = (
        select(SessionTurn)
        .where(SessionTurn.session_id == session_id)
        .order_by(SessionTurn.id.desc())
        .limit(settings.history_turns * 2)
    )
    with _lock, Session(_engine) as session:
        rows = session.scalars(query).all()
    return [Turn(role=r.role, content=r.content) for r in reversed(rows)]


def append_exchange(session_id: str, user_message: str, reply: str) -> None:
    with _lock, Session(_engine) as session:
        session.add_all(
            [
                SessionTurn(session_id=session_id, role="user", content=user_message),
                SessionTurn(session_id=session_id, role="assistant", content=reply),
            ]
        )
        session.flush()
        newest = (
            select(SessionTurn.id)
            .where(SessionTurn.session_id == session_id)
            .order_by(SessionTurn.id.desc())
            .limit(settings.history_turns * 2)
        )
        session.execute(delete(SessionTurn).where(SessionTurn.session_id == session_id, SessionTurn.id.not_in(newest)))
        session.commit()


def clear_all() -> None:
    with _lock, Session(_engine) as session:
        session.execute(delete(SessionTurn))
        session.commit()
