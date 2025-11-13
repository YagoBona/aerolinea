from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from vuelos.models import Reserva, Vuelo, Asiento, Pasajero


def crear_reserva(pasajero_id, vuelo_id, asiento_id):
    """Crea una reserva de forma atómica. Lanza ValidationError si no es posible."""
    with transaction.atomic():
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        asiento = get_object_or_404(Asiento, id=asiento_id, avion=vuelo.avion)
        # lock asiento row to avoid concurrent bookings
        asiento = Asiento.objects.select_for_update().get(id=asiento.id)

        ocupada = Reserva.objects.filter(
            vuelo=vuelo, asiento=asiento, estado__in=['confirmada', 'pendiente']
        ).exists()
        if ocupada:
            raise ValidationError("Asiento no disponible para ese vuelo")

        reserva = Reserva.objects.create(
            pasajero=pasajero,
            vuelo=vuelo,
            asiento=asiento,
            estado='pendiente'
        )
        return reserva
