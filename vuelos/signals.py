from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Avion, Asiento

@receiver(post_save, sender=Avion)
def crear_asientos(sender, instance, created, **kwargs):
    if created:
        for fila in range(1, instance.filas + 1):
            for columna in range(1, instance.columnas + 1):
                numero = f"{fila}{chr(64 + columna)}"  # Ej: 1A, 1B, 2A...
                Asiento.objects.create(
                    avion=instance,
                    numero=numero,
                    fila=fila,
                    columna=columna,
                    tipo='estándar',  # Podés hacer lógica para diferenciar tipos
                    estado='disponible'
                )
    