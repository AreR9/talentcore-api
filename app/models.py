from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    Session,
)

from pydantic import BaseModel, ConfigDict, Field

SQLALCHEMY_DATABASE_URL = "sqlite:///./talentcore.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    rol = Column(String, nullable=False)  # EMPLADO | MANAGER | ADMIN_RRHH
    anios_antiguedad = Column(Integer, nullable=False, default=1)
    manager_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    manager = relationship("Empleado", remote_side=[id], backref="subordinados")
    solicitudes = relationship(
        "SolicitudVacaciones",
        back_populates="empleado",
        foreign_keys="SolicitudVacaciones.empleado_id",
    )
    revisiones = relationship(
        "SolicitudVacaciones",
        back_populates="revisado_por",
        foreign_keys="SolicitudVacaciones.revisado_por_id",
    )


class SolicitudVacaciones(Base):
    __tablename__ = "solicitudes_vacaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    dias_solicitados = Column(Integer, nullable=False)
    motivo = Column(String, nullable=True)
    estado = Column(String, nullable=False, default="PENDING")  # PENDING | APPROVED | REJECTED
    revisado_por_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("dias_solicitados > 0", name="ck_dias_positivos"),
        UniqueConstraint("id"),
    )

    empleado = relationship(
        "Empleado", back_populates="solicitudes", foreign_keys=[empleado_id]
    )
    revisado_por = relationship(
        "Empleado", back_populates="revisiones", foreign_keys=[revisado_por_id]
    )


class EmpleadoCreate(BaseModel):
    nombre: str
    email: str
    rol: str = Field(..., pattern="^(EMPLEADO|MANAGER|ADMIN_RRHH)$")
    anios_antiguedad: int
    manager_id: Optional[int] = None


class EmpleadoResponse(EmpleadoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SaldoResponse(BaseModel):
    empleado_id: int
    dias_totales: int
    dias_aprobados: int
    saldo_disponible: int
    model_config = ConfigDict(from_attributes=True)


class SolicitudCreate(BaseModel):
    empleado_id: int
    dias_solicitados: int = Field(..., gt=0)
    motivo: Optional[str] = None


class RevisionRequest(BaseModel):
    accion: str = Field(..., pattern="^(APPROVE|REJECT)$")


class SolicitudResponse(BaseModel):
    id: int
    empleado_id: int
    dias_solicitados: int
    motivo: Optional[str] = None
    estado: str
    revisado_por_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
