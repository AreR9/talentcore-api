# 🏢 TalentCore API - Microservicio de Gestión de Vacaciones

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Build Status](https://github.com/AreR9/talentcore-api/workflows/TalentCore%20CI/badge.svg)

Microservicio RESTful desarrollado en **FastAPI** para la gestión automatizada de empleados, cálculo de saldos de vacaciones según la antigüedad y flujo jerárquico de aprobaciones mediante control de acceso basado en roles (RBAC).

---

## 🌐 Demo e Interacción en Vivo

La API se encuentra desplegada y totalmente funcional en Render:

* 🔗 **Swagger UI Interactivo:** [https://talentcore-api-areli-reynoso.onrender.com/docs](https://talentcore-api-areli-reynoso.onrender.com/docs)
* 💚 **Health Check Endpoint:** `GET https://talentcore-api-areli-reynoso.onrender.com/health`

---

## 🚀 Características Principales

* **Reglas de Negocio Legales:** Cálculo dinámico de saldo acumulado con la fórmula $\min(12 + 2 \times (\text{años} - 1), 20)$.
* **Control de Acceso RBAC:** Validación jerárquica con encabezados `X-User-Id` para evitar accesos no autorizados (mitigación BOLA/OWASP).
* **Entorno Inmutable con Docker:** Empaquetado completo con `Dockerfile` y `docker-compose.yml`.
* **Pruebas Automatizadas (CI):** Integración continua en GitHub Actions ejecutando suites con `pytest`.

---

## 🛠️ Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/AreR9/talentcore-api.git](https://github.com/AreR9/talentcore-api.git)
   cd talentcore-api
