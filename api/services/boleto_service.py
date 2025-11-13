import uuid
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from vuelos.models import Reserva, Boleto


def generar_boleto_desde_reserva(reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if reserva.estado != 'confirmada':
        raise ValidationError("Solo se puede generar boleto a partir de una reserva confirmada")
    codigo = uuid.uuid4().hex
    boleto = Boleto.objects.create(
        reserva=reserva,
        codigo_barra=codigo
    )
    return boleto
