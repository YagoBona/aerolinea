from django.shortcuts import render, get_object_or_404, redirect
from .models import Vuelo, Asiento, Reserva, Pasajero
from django.utils import timezone
import uuid
from vuelos.forms import FormularioRegistro
from django.contrib.auth import login
from .models import Usuario
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Usuario, Pasajero, Boleto


def lista_vuelos(request):
    vuelos = Vuelo.objects.select_related('avion').all()
    return render(request, 'vuelos/lista_vuelos.html', {'vuelos': vuelos})

def detalle_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    asientos = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')
    reservas = Reserva.objects.filter(vuelo=vuelo)
    return render(request, 'vuelos/detalle_vuelo.html', {
        'vuelo': vuelo,
        'asientos': asientos,
        'reservas': reservas
    })

@login_required
def reservar_asiento(request, vuelo_id, asiento_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    asiento = get_object_or_404(Asiento, id=asiento_id)

    if asiento.estado != 'disponible':
        return render(request, 'vuelos/error.html', {'mensaje': 'El asiento ya está reservado.'})

    pasajero = Pasajero.objects.get(usuario=request.user)

    if request.method == 'POST':
        reserva = Reserva.objects.create(
            vuelo=vuelo,
            pasajero=pasajero,
            asiento=asiento,
            estado='confirmada',
            precio=vuelo.precio_base,
            codigo_reserva=str(uuid.uuid4())
        )

        asiento.estado = 'reservado'
        asiento.save()

        boleto = Boleto.objects.create(
            reserva=reserva,
            codigo_barra=str(uuid.uuid4())[:12]
        )

        return render(request, 'vuelos/confirmacion.html', {
            'reserva': reserva,
            'boleto': boleto
        })

    return redirect('detalle_vuelo', vuelo_id=vuelo.id)




def registro_usuario(request):
    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()

            Pasajero.objects.create(
                usuario=user,
                nombre=user.username,
                documento=user.username,
                email=user.email,
                telefono='0000',
                fecha_nacimiento='2000-01-01',
                tipo_documento='DNI'
            )

            login(request, user)
            return redirect('mis_reservas')
    else:
        form = FormularioRegistro()

    return render(request, 'vuelos/registro.html', {'form': form})

@login_required
def mis_reservas(request):
    pasajero = Pasajero.objects.filter(documento=request.user.username).first()
    reservas = Reserva.objects.filter(pasajero=pasajero).select_related('vuelo', 'asiento') if pasajero else []
    return render(request, 'vuelos/mis_reservas.html', {'reservas': reservas})

@login_required
def ver_boleto(request, codigo_reserva):
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    
    # Seguridad: asegurarse de que el usuario accede solo a su reserva
    if reserva.pasajero.usuario != request.user:
        return render(request, 'vuelos/error.html', {'mensaje': 'No tenés permiso para ver este boleto.'})

    boleto = getattr(reserva, 'boleto', None)
    return render(request, 'vuelos/confirmacion.html', {
        'reserva': reserva,
        'boleto': boleto
    })

@login_required
def imprimir_boleto(request, codigo_reserva):
    reserva = get_object_or_404(Reserva, codigo_reserva=codigo_reserva)
    if reserva.pasajero.usuario != request.user:
        return render(request, 'vuelos/error.html', {'mensaje': 'No tenés permiso para ver este boleto.'})

    boleto = getattr(reserva, 'boleto', None)
    return render(request, 'vuelos/boleto_imprimible.html', {
        'reserva': reserva,
        'boleto': boleto
    })

