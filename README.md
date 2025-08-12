# Aerolíneas Yager

Sistema web para gestión de reservas y emisión de boletos electrónicos de vuelos.

## Requisitos
- Python 3.10+
- Django 5+
- SQLite (por defecto)

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
