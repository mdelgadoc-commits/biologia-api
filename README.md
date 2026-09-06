# Biología API - Backend

API Backend desarrollada en Django REST Framework para la plataforma educativa interactiva de Biología.

## Configuración y Comandos Principales

* **Iniciar Servidor:**
  ```bash
  source venv/bin/activate
  python manage.py migrate
  python manage.py runserver
  ```

* **Poblar Datos de Prueba (Seeder):**
  ```bash
  python manage.py seed_demo
  ```
  Genera automáticamente un docente (docente_demo / demo1234), una sección con 5 estudiantes y un historial con múltiples intentos para pruebas de reporte.

* **Ejecutar Suite de Pruebas:**
  ```bash
  python manage.py test
  ```

---

## Arquitectura de Software: Funciones Stateless vs Stateful

| Componente | Tipo | Ubicación | Descripción / Evidencia |
|---|---|---|---|
| calcular_estrellas_por_vidas | Stateless | apps/gamificacion/calculos.py | Cálculo matemático determinista sin dependencias externas. |
| calcular_monedas_recompensa | Stateless | apps/gamificacion/calculos.py | Fórmula pura de bonificación y penalización. |
| useCronometro | Stateful | src/composables/useCronometro.js | Estado de tiempo reactivo en el frontend. |
| registrar_respuesta | Stateful | apps/intentos/services.py | Modificación acumulativa basada en historial de la BD. |
| obtener_resumen_cacheado | Stateful | apps/gamificacion/cache_reportes.py | Respuesta condicional a la ventana TTL del caché (desde_cache). |

> La documentación detallada con análisis arquitectónico y pruebas se encuentra en [docs/ARQUITECTURA_STATELESS_STATEFUL.md](docs/ARQUITECTURA_STATELESS_STATEFUL.md).
