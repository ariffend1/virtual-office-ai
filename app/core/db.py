import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, select
from app.core.config import settings, DEFAULT_AGENT_PROFILES
from app.models.db_models import AgentDB

DB_FILE = settings.base_dir / "cortxos.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

def init_db():
    """Create database tables and seed initial agent profiles if empty."""
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_agents = session.exec(select(AgentDB)).all()
        if not existing_agents:
            for agent_id, profile in DEFAULT_AGENT_PROFILES.items():
                agent = AgentDB(
                    id=profile["id"],
                    name=profile["name"],
                    role=profile["role"],
                    color=profile["color"],
                    capabilities=profile["capabilities"],
                    status=profile.get("status", "ready")
                )
                session.add(agent)
            session.commit()

def get_session():
    """Dependency / helper to yield database session."""
    with Session(engine) as session:
        yield session
