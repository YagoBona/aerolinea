from django.db import models
from django.conf import settings

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField()
    filas = models.PositiveIntegerField()
    columnas = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.modelo} ({self.capacidad} asientos)"

class Vuelo(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado')
    ]

    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField()
    estado = models.CharField(max_length=20, choices=ESTADOS)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.origen} → {self.destino} - {self.fecha_salida.strftime('%Y-%m-%d %H:%M')}"

class Pasajero(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    tipo_documento = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nombre} ({self.documento})"

class Asiento(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('ocupado', 'Ocupado')
    ]

    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)
    numero = models.CharField(max_length=5)
    fila = models.IntegerField()
    columna = models.IntegerField()
    tipo = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return f"Asiento {self.numero} - {self.avion.modelo}"


import uuid

class Reserva(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.OneToOneField(Asiento, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"Reserva {self.codigo_reserva}"


class Boleto(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    codigo_barra = models.CharField(max_length=100)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"Boleto de {self.reserva.pasajero.nombre}"


from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
        ('cliente', 'Cliente')
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.rol})"
