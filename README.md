# Aerolíneas Yager

Sistema web para gestión de reservas y emisión de boletos electrónicos de vuelos.

## Requisitos
- Python 3.10+
- Django 5+
- SQLite (por defecto)

Requisitos (Parte 2 - API)
- La Parte 2 añade una API REST implementada con Django REST Framework y dependencias asociadas.
- Para la Parte 2 instala las siguientes dependencias (ya incluidas en `requirements.txt`):
   - `djangorestframework>=3.15`
   - `drf-yasg>=1.21.0` (Swagger / Redoc)
   - `requests>=2.28` (útil para scripts y pruebas)
   - Para pruebas: `pytest`, `pytest-django`
- Instálalas con:

```sh
pip install -r requirements.txt
```

## Instalación
1. Clona el repositorio o descarga los archivos.
2. Crea y activa un entorno virtual:
   ```sh
   python -m venv env
   env\Scripts\activate
   ```
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Aplica migraciones:
   ```sh
   python manage.py migrate
   ```
5. (Opcional) Crea un superusuario para el admin:
   ```sh
   python manage.py createsuperuser
   ```
6. Ejecuta el servidor:
   ```sh
   python manage.py runserver
   ```
7. Accede a la web en [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Funcionalidades
- Registro e inicio de sesión de usuarios
- Visualización de vuelos disponibles
- Reserva de asientos
- Emisión de boletos electrónicos
- Panel de usuario con reservas
- Panel de administración (Django admin)

## Estructura
- `aerolinea/` : Configuración principal Django
- `vuelos/` : App principal (modelos, vistas, templates)
- `templates/vuelos/` : HTML y diseño
- `db.sqlite3` : Base de datos

## Personalización
- Colores y estilos en naranja
- Boleto electrónico moderno
- Mensajes de error amigables

## Contacto
Para soporte, contacta al equipo de desarrollo.

## API (Parte 2) — Django REST Framework

Se agregó una API REST para exponer las funcionalidades principales: gestión de aviones, vuelos, pasajeros, asientos, reservas y boletos.

- Base URL: `http://127.0.0.1:8000/api/`
- Documentación Swagger: `http://127.0.0.1:8000/swagger/`
- Redoc: `http://127.0.0.1:8000/redoc/`

Endpoints principales (resumen):

- `POST /api/auth-token/` : obtener token (body: `username`, `password`).
- `GET /api/vuelos/` : listar vuelos.
- `GET /api/vuelos/{id}/` : detalle de un vuelo.
- `GET /api/aviones/` : listar aviones.
- `GET /api/aviones/{id}/layout/` : obtener el layout (asientos) de un avión.
- `GET /api/asientos/` : listar asientos.
- `GET /api/pasajeros/` : listar pasajeros (crear también disponible para registro).
- `POST /api/reservas/crear/` : crear reserva (body: `pasajero`, `vuelo`, `asiento` — IDs).
- `POST /api/reservas/{id}/confirmar/` : confirmar reserva (genera boleto si corresponde).
- `POST /api/reservas/{id}/cancelar/` : cancelar reserva.
- `GET /api/boletos/` : listar boletos.

Autenticación
- La API usa `TokenAuthentication` (app `rest_framework.authtoken`).
- Obtén un token con `POST /api/auth-token/` (usuario y contraseña).
- Para usar el token en peticiones: añade el header `Authorization: Token <tu_token>`.

Ejemplos de Postman (resumen)

Puedes importar la colección `api/postman_collection.json` incluida en el repositorio o crear requests manuales. A continuación hay ejemplos listos para pegar como bodies/headers en Postman (usa `{{baseUrl}}` y `{{token}}` como variables de entorno si quieres):

1) Obtener token
- Método: `POST`
- URL: `{{baseUrl}}/api/auth-token/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):

```json
{
   "username": "admin",
   "password": "tu_password"
}
```

Respuesta esperada: `{ "token": "..." }` — copia el token a `{{token}}`.

2) Crear reserva
- Método: `POST`
- URL: `{{baseUrl}}/api/reservas/crear/`
- Headers:
   - `Content-Type: application/json`
   - `Authorization: Token {{token}}`
- Body (raw JSON):

```json
{
   "pasajero": 3,
   "vuelo": 5,
   "asiento": 12,
   "precio": "150.00"
}
```

3) Confirmar reserva
- Método: `POST`
- URL: `{{baseUrl}}/api/reservas/{{reserva_id}}/confirmar/`
- Headers: `Authorization: Token {{token}}`

Respuesta esperada: objeto con `reserva` y `boleto` (contiene `codigo_barra`).

4) Cancelar reserva
- Método: `POST`
- URL: `{{baseUrl}}/api/reservas/{{reserva_id}}/cancelar/`
- Headers: `Authorization: Token {{token}}`

Notas rápidas
- Si prefieres, importa `api/postman_collection.json` y rellena las variables del entorno (`baseUrl`, `token`, `pasajero_id`, `vuelo_id`, `asiento_id`, `reserva_id`).

Notas importantes
- La creación de reservas aplica bloqueo a nivel de fila para evitar doble reserva del mismo asiento (`transaction.atomic()` y `select_for_update()`).
- Al confirmar una reserva se genera un `Boleto` asociado; solo reservas con estado `confirmada` generan boleto.
- Los endpoints que modifican datos requieren autenticación; algunos registros (como crear pasajero) permiten `AllowAny` para registro.

Pruebas recomendadas
- Crear dos sesiones (dos usuarios) y tratar de reservar el mismo asiento simultáneamente para verificar que no se permiten dobles reservas.
- Probar flujo completo: crear reserva -> confirmar -> verificar que se generó un boleto.

