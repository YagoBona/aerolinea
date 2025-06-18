from django.contrib import admin
from .models import Avion, Vuelo, Pasajero, Asiento, Reserva, Boleto, Usuario
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'capacidad', 'filas', 'columnas')

@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'fecha_salida', 'estado', 'avion')
    list_filter = ('estado', 'fecha_salida')
    search_fields = ('origen', 'destino')

@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'email', 'telefono')
    search_fields = ('nombre', 'documento')

@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'avion', 'fila', 'columna', 'estado')
    list_filter = ('avion', 'estado')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo_reserva', 'pasajero', 'vuelo', 'asiento', 'estado', 'precio')
    list_filter = ('estado',)

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'codigo_barra', 'fecha_emision', 'estado')

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol personalizado', {'fields': ('rol',)}),
    )
