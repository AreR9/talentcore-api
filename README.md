<div align="center">

# 🏢 TalentCore API

### Microservicio de Gestión de Vacaciones

Gestión automatizada de empleados, cálculo de saldos según antigüedad y flujo jerárquico de aprobaciones con control de acceso por roles.

<br>

[![Swagger UI](https://img.shields.io/badge/📘_Swagger_UI-Probar_API-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://talentcore-api-areli-reynoso.onrender.com/docs)
[![Health Check](https://img.shields.io/badge/💚_Health-Check-2ea44f?style=for-the-badge)](https://talentcore-api-areli-reynoso.onrender.com/health)

![Build Status](https://github.com/AreR9/talentcore-api/workflows/TalentCore%20CI/badge.svg)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)

</div>

---

## 🌐 Demo en vivo

La API está desplegada y funcionando en **Render**:

| Recurso | Enlace |
|:---|:---|
| 📘 **Swagger UI interactivo** | [/docs](https://talentcore-api-areli-reynoso.onrender.com/docs) |
| 💚 **Health Check** | `GET` [/health](https://talentcore-api-areli-reynoso.onrender.com/health) |

> ⏳ **Nota:** el plan gratuito de Render "duerme" la app tras un rato sin uso. La primera petición puede tardar ~30-50 segundos en responder.

---

## 🚀 Características principales

| | Característica | Detalle |
|:---:|:---|:---|
| ⚖️ | **Reglas de negocio legales** | Cálculo dinámico del saldo de vacaciones según antigüedad |
| 🔐 | **Control de acceso RBAC** | Validación jerárquica con el encabezado `X-User-Id`; mitiga **BOLA** (OWASP) |
| 🐳 | **Entorno inmutable** | Empaquetado con `Dockerfile` y `docker-compose.yml` |
| ✅ | **Integración continua** | Pruebas con `pytest` ejecutadas en **GitHub Actions** |

### 📐 Fórmula de vacaciones

$$
\text{días} = \min\bigl(12 + 2 \times (\text{años} - 1),\ 20\bigr)
$$

<details>
<summary><b>📝 Ver ejemplos de cálculo</b></summary>

<br>

| Antigüedad | Días de vacaciones |
|:---:|:---:|
| 1 año | 12 |
| 2 años | 14 |
| 3 años | 16 |
| 4 años | 18 |
| 5 años o más | 20 *(tope)* |

</details>

---

## 🧰 Stack tecnológico

| Capa | Tecnología |
|:---|:---|
| Framework | FastAPI |
| Lenguaje | Python |
| Contenedores | Docker · Docker Compose |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Despliegue | Render |

---

## 🛠️ Ejecución local

### Opción 1: Con Docker 🐳 (recomendada)

```bash
# 1. Clonar el repositorio
git clone https://github.com/AreR9/talentcore-api.git
cd talentcore-api

# 2. Levantar el servicio
docker-compose up --build
```

### Opción 2: Con Python 🐍

```bash
# 1. Clonar el repositorio
git clone https://github.com/AreR9/talentcore-api.git
cd talentcore-api

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el servidor
uvicorn app.main:app --reload
```

Abre **http://localhost:8000/docs** para ver la documentación interactiva.

---

## 🧪 Pruebas

```bash
pytest
```

Las pruebas también se ejecutan automáticamente en cada `push` mediante **GitHub Actions**.

---

## 🔑 Autenticación

Los endpoints protegidos requieren el encabezado:

```http
X-User-Id: <id_del_usuario>
```

El rol del usuario determina qué recursos puede consultar y qué solicitudes puede aprobar.

---

<div align="center">

### 👩‍💻 Desarrollado por **Areli Reynoso**

[![GitHub](https://img.shields.io/badge/GitHub-AreR9-181717?style=flat-square&logo=github)](https://github.com/AreR9)

⭐ Si te gustó el proyecto, ¡dale una estrella!

</div>
