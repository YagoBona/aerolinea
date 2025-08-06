from django.shortcuts import render, get_object_or_404, redirect
from .models import Vuelo, Asiento, Reserva, Pasajero
from django.utils import timezone
import uuid
from vuelos.forms import FormularioRegistro
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Usuario, Pasajero, Boleto
from django.views.decorators.http import require_POST

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

    # Verificar si el asiento ya tiene una reserva
    from vuelos.models import Reserva
    if Reserva.objects.filter(asiento=asiento).exists() or asiento.estado != 'disponible':
        return render(request, 'vuelos/error.html', {'mensaje': 'El asiento ya está reservado.'})

    try:
        pasajero = Pasajero.objects.get(usuario=request.user)
    except Pasajero.DoesNotExist:
        return render(request, 'vuelos/error.html', {'mensaje': 'No se encontró el perfil de pasajero para el usuario actual. Por favor, registrate como pasajero.'})

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
            dni = form.cleaned_data['dni']  # <- obtenemos el dato

            Pasajero.objects.create(
                usuario=user,
                nombre=user.username,
                documento=dni,  # <- lo usamos
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
    pasajero = Pasajero.objects.filter(usuario=request.user).first()
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


@require_POST
@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, pasajero__usuario=request.user)

    if reserva.estado != 'cancelada':
        reserva.estado = 'cancelada'
        reserva.save()

        reserva.asiento.estado = 'disponible'
        reserva.asiento.save()

    return redirect('mis_reservas')

def inicio(request):
    from .models import Vuelo
    vuelos = Vuelo.objects.filter(estado='activo').order_by('fecha_salida')
    return render(request, 'vuelos/inicio.html', {'vuelos': vuelos})