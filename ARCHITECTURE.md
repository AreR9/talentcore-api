# ARCHITECTURE.md  

## 1. MODELO DE DATOS (SQLite / SQLAlchemy)

```python
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    rol = Column(String, nullable=False)  # 'EMPLEADO' | 'MANAGER' | 'ADMIN_RRHH'
    anios_antiguedad = Column(Integer, nullable=False, default=1)
    manager_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    manager = relationship("Empleado", remote_side=[id], backref="subordinados")
    solicitudes = relationship(
        "SolicitudVacaciones", back_populates="empleado", cascade="all, delete-orphan"
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
    estado = Column(
        String,
        nullable=False,
        default="PENDING",
    )  # 'PENDING' | 'APPROVED' | 'REJECTED'
    revisado_por_id = Column(Integer, ForeignKey("empleados.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("dias_solicitados > 0", name="ck_dias_positive"),
    )

    empleado = relationship("Empleado", back_populates="solicitudes")
    revisado_por = relationship(
        "Empleado", back_populates="revisiones", foreign_keys=[revisado_por_id]
    )
```

*Only the two tables above exist; no JWT or extra tables are defined.*

---

## 2. ESQUEMAS PYDANTIC V2

```python
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, validator


class EmpleadoCreate(BaseModel):
    nombre: str
    email: str
    rol: str  # must be one of the three values
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
    accion: str

    @validator("accion")
    def check_accion(cls, v):
        if v not in {"APPROVE", "REJECT"}:
            raise ValueError("accion must be 'APPROVE' or 'REJECT'")
        return v


class SolicitudResponse(BaseModel):
    id: int
    empleado_id: int
    dias_solicitados: int
    motivo: Optional[str] = None
    estado: str
    revisado_por_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
```

---

## 3. ENDPOINTS REST Y RBAC (Header `X-User-Id: int`)

| Método | Ruta | Descripción | RBAC / Validaciones | Respuestas |
|--------|------|-------------|---------------------|------------|
| `GET` | `/health` | Salud del servicio | Público | `200 {"status":"ok"}` |
| `POST` | `/api/v1/empleados` | Crear empleado | - Si **no hay** registros → permite crear primer `ADMIN_RRHH` sin validar rol.<br>- Si existen empleados → `X-User-Id` debe referir a un empleado con `rol=="ADMIN_RRHH"`; de lo contrario `403`.<br>- Si `X-User-Id` no existe → `404` | `201 EmpleadoResponse` |
| `GET` | `/api/v1/vacaciones/saldo/{empleado_id}` | Calcular saldo | `X-User-Id` debe existir; si no → `404`. No se verifica que el solicitante sea el mismo empleado (solo lectura). | `200 SaldoResponse` |
| `POST` | `/api/v1/vacaciones/solicitar` | Crear solicitud en `PENDING` | Header user must exist (`404` if not). `empleado_id` in body must equal `X-User-Id` (otherwise `403`). Compute `saldo_disponible`; if `dias_solicitados` > saldo → `400 {"detail":"Insufficient vacation balance"}`. | `201 SolicitudResponse` |
| `POST` | `/api/v1/vacaciones/{solicitud_id}/revisar` | Aprobar o rechazar | - Header user must exist and have `rol=="MANAGER"`; else `403`.<br>- Must be direct manager: `solicitud.empleado.manager_id == X-User-Id`; else `403 {"detail":"Unauthorized: Not the direct manager"}`.<br>- Solicitud must be in `PENDING`; otherwise `400`.<br>- On success set `estado` según `accion`, `revisado_por_id = X-User-Id`. | `200 SolicitudResponse` |

### Lógica de cálculo de saldo (usada en `/saldo` y en la validación de solicitud)

```python
def dias_totales(anios: int) -> int:
    if anios >= 1:
        return min(12 + 2 * (anios - 1), 20)
    return 12


def saldo(empleado: Empleado, db: Session) -> dict:
    total = dias_totales(empleado.anios_antiguedad)
    aprobadas = (
        db.query(func.sum(SolicitudVacaciones.dias_solicitados))
        .filter(
            SolicitudVacaciones.empleado_id == empleado.id,
            SolicitudVacaciones.estado == "APPROVED",
        )
        .scalar()
        or 0
    )
    disponible = total - aprobadas
    return {
        "empleado_id": empleado.id,
        "dias_totales": total,
        "dias_aprobados": aprobadas,
        "saldo_disponible": disponible,
    }
```

All routes raise `HTTPException` with appropriate status codes (`404`, `403`, `400`, `201`, `200`). No JWT, no extra middleware; authentication is solely the integer header `X-User-Id`.