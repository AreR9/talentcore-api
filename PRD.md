## 1. ROLES DEL SISTEMA
- **EMPLEADO**: consulta su saldo y envía solicitudes de vacaciones para sí mismo.  
- **MANAGER**: aprueba o rechaza solicitudes **únicamente** de sus subordinados directos (`empleado.manager_id == manager.id`).  
- **ADMIN_RRHH**: crea y actualiza registros de empleados.

## 2. REGLA DE SALDO DE VACACIONES
- **Cálculo de días totales**:  
  ```
  if anios_antiguedad >= 1:
      dias_totales = min(12 + 2 * (anios_antiguedad - 1), 20)
  else:
      dias_totales = 12
  ```
- **Saldo disponible**: `dias_totales - Σ(dias_solicitados en estado APPROVED)`.

## 3. MÁQUINA DE ESTADOS DE SOLICITUD
| Estado   | Transición permitida                     |
|----------|------------------------------------------|
| PENDING  | Estado inicial al crear la solicitud.   |
| APPROVED | Sólo desde PENDING; descuenta saldo.    |
| REJECTED | Sólo desde PENDING; no descuenta saldo. |

*Solo solicitudes en **PENDING** pueden ser revisadas (aprobar/rechazar).*

## 4. CRITERIOS DE ACEPTACIÓN (Gherkin compacto)

```gherkin
Feature: Gestión de vacaciones

  Scenario: AC-01 Solicitud válida con saldo suficiente
    Given employee "E1" has 5 days available
    When employee "E1" POST "/vacations" with { "days": 3 }
    Then response status is 201
    And response body contains "status": "PENDING"

  Scenario: AC-02 Solicitud rechazada por saldo insuficiente
    Given employee "E2" has 2 days available
    When employee "E2" POST "/vacations" with { "days": 4 }
    Then response status is 400
    And response body.detail is "Insufficient vacation balance"

  Scenario: AC-03 Manager revisa solicitud de no subordinado
    Given manager "M1" manages employee "E3"
    And employee "E4" (not managed by "M1") has a pending request "R1"
    When manager "M1" PATCH "/vacations/R1" with { "action": "APPROVE" }
    Then response status is 403
    And response body.detail is "Unauthorized: Not the direct manager"
```