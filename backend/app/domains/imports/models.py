import enum
from typing import Optional
from sqlalchemy import String, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    source_url: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)

    logs = relationship("ImportLog", back_populates="job", cascade="all, delete-orphan")

class ImportLog(Base):
    __tablename__ = "import_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("import_jobs.id"))
    source_url: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus))
    raw_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_prompt_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job = relationship("ImportJob", back_populates="logs")
