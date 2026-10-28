import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ac01_solicitud_valida_y_calculo_saldo():
    # crear ADMIN_RRHH
    admin_payload = {
        "nombre": "Admin",
        "email": "admin@example.com",
        "rol": "ADMIN_RRHH",
        "anios_antiguedad": 5,
        "manager_id": None,
    }
    resp = client.post("/api/v1/empleados", json=admin_payload)
    assert resp.status_code == 201
    admin_id = resp.json()["id"]
    assert admin_id == 1

    # crear MANAGER con header X-User-Id=1
    manager_payload = {
        "nombre": "Manager",
        "email": "manager@example.com",
        "rol": "MANAGER",
        "anios_antiguedad": 2,
        "manager_id": None,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=manager_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    manager_id = resp.json()["id"]
    assert manager_id == 2

    # crear EMPLEADO con manager_id=2 y anios_antiguedad=3
    empleado_payload = {
        "nombre": "Empleado",
        "email": "empleado@example.com",
        "rol": "EMPLEADO",
        "anios_antiguedad": 3,
        "manager_id": manager_id,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=empleado_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    empleado_id = resp.json()["id"]
    assert empleado_id == 3

    # verificar saldo inicial
    resp = client.get(f"/api/v1/vacaciones/saldo/{empleado_id}")
    assert resp.status_code == 200
    saldo = resp.json()
    assert saldo["dias_totales"] == 16
    assert saldo["saldo_disponible"] == 16

    # solicitar 5 días
    solicitud_payload = {"empleado_id": empleado_id, "dias_solicitados": 5}
    resp = client.post(
        "/api/v1/vacaciones/solicitar", json=solicitud_payload
    )
    assert resp.status_code == 201
    solicitud = resp.json()
    assert solicitud["estado"] == "PENDING"
    solicitud_id = solicitud["id"]
    assert solicitud_id == 1

    # manager aprueba
    revisar_payload = {"accion": "APPROVE"}
    resp = client.post(
        f"/api/v1/vacaciones/{solicitud_id}/revisar",
        json=revisar_payload,
        headers={"X-User-Id": str(manager_id)},
    )
    assert resp.status_code == 200
    revisada = resp.json()
    assert revisada["estado"] == "APPROVED"
    assert revisada["revisado_por_id"] == manager_id

    # verificar saldo actualizado
    resp = client.get(f"/api/v1/vacaciones/saldo/{empleado_id}")
    assert resp.status_code == 200
    saldo = resp.json()
    assert saldo["saldo_disponible"] == 11


def test_ac02_saldo_insuficiente():
    # crear ADMIN_RRHH
    admin_payload = {
        "nombre": "Admin2",
        "email": "admin2@example.com",
        "rol": "ADMIN_RRHH",
        "anios_antiguedad": 5,
        "manager_id": None,
    }
    resp = client.post("/api/v1/empleados", json=admin_payload)
    assert resp.status_code == 201
    admin_id = resp.json()["id"]

    # crear EMPLEADO con anios_antiguedad=1 (12 días)
    empleado_payload = {
        "nombre": "Empleado2",
        "email": "empleado2@example.com",
        "rol": "EMPLEADO",
        "anios_antiguedad": 1,
        "manager_id": None,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=empleado_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    empleado_id = resp.json()["id"]

    # intentar solicitar 15 días (más que 12)
    solicitud_payload = {"empleado_id": empleado_id, "dias_solicitados": 15}
    resp = client.post(
        "/api/v1/vacaciones/solicitar", json=solicitud_payload
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Insufficient vacation balance"


def test_ac03_manager_no_autorizado():
    # crear ADMIN_RRHH
    admin_payload = {
        "nombre": "Admin3",
        "email": "admin3@example.com",
        "rol": "ADMIN_RRHH",
        "anios_antiguedad": 5,
        "manager_id": None,
    }
    resp = client.post("/api/v1/empleados", json=admin_payload)
    assert resp.status_code == 201
    admin_id = resp.json()["id"]

    # crear MANAGER A
    manager_a_payload = {
        "nombre": "ManagerA",
        "email": "managerA@example.com",
        "rol": "MANAGER",
        "anios_antiguedad": 2,
        "manager_id": None,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=manager_a_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    manager_a_id = resp.json()["id"]

    # crear MANAGER B
    manager_b_payload = {
        "nombre": "ManagerB",
        "email": "managerB@example.com",
        "rol": "MANAGER",
        "anios_antiguedad": 2,
        "manager_id": None,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=manager_b_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    manager_b_id = resp.json()["id"]

    # crear EMPLEADO con manager_id = manager_a_id
    empleado_payload = {
        "nombre": "Empleado3",
        "email": "empleado3@example.com",
        "rol": "EMPLEADO",
        "anios_antiguedad": 1,
        "manager_id": manager_a_id,
    }
    resp = client.post(
        "/api/v1/empleados",
        json=empleado_payload,
        headers={"X-User-Id": str(admin_id)},
    )
    assert resp.status_code == 201
    empleado_id = resp.json()["id"]

    # empleado solicita 3 días
    solicitud_payload = {"empleado_id": empleado_id, "dias_solicitados": 3}
    resp = client.post(
        "/api/v1/vacaciones/solicitar", json=solicitud_payload
    )
    assert resp.status_code == 201
    solicitud_id = resp.json()["id"]
    assert solicitud_id == 1

    # manager B intenta aprobar
    revisar_payload = {"accion": "APPROVE"}
    resp = client.post(
        f"/api/v1/vacaciones/{solicitud_id}/revisar",
        json=revisar_payload,
        headers={"X-User-Id": str(manager_b_id)},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Unauthorized: Not the direct manager"
