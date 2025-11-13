from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Avion, Vuelo, Asiento, Pasajero, Reserva, Boleto

User = get_user_model()


class ApiReservationFlowTests(TestCase):
    def setUp(self):
        # usuario y pasajero
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.pasajero = Pasajero.objects.create(
            usuario=self.user,
            nombre='Test User',
            documento='12345678',
            email='test@example.com',
            telefono='123456',
            fecha_nacimiento='1990-01-01',
            tipo_documento='DNI'
        )

        # avion, asientos y vuelo
        self.avion = Avion.objects.create(modelo='A320', capacidad=6, filas=2, columnas=3)
        # crear asientos para el avión
        self.asiento1 = Asiento.objects.create(avion=self.avion, numero='1A', fila=1, columna=1, tipo='economica')
        self.asiento2 = Asiento.objects.create(avion=self.avion, numero='1B', fila=1, columna=2, tipo='economica')

        now = timezone.now()
        self.vuelo = Vuelo.objects.create(
            avion=self.avion,
            origen='A',
            destino='B',
            fecha_salida=now + timedelta(days=1),
            fecha_llegada=now + timedelta(days=1, hours=2),
            duracion=timedelta(hours=2),
            estado='activo',
            precio_base='100.00'
        )

        self.client = APIClient()

    def test_token_and_reservation_create_confirm_cancel(self):
        # obtener token
        resp = self.client.post('/api/auth-token/', {'username': 'testuser', 'password': 'pass'}, format='json')
        self.assertEqual(resp.status_code, 200)
        token = resp.data.get('token')
        self.assertIsNotNone(token)

        # usar token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # crear reserva
        create_resp = self.client.post('/api/reservas/crear/', {
            'pasajero': self.pasajero.id,
            'vuelo': self.vuelo.id,
            'asiento': self.asiento1.id
        }, format='json')
        self.assertIn(create_resp.status_code, (200, 201))
        reserva_id = create_resp.data.get('id')
        self.assertIsNotNone(reserva_id)

        # cancelar reserva
        cancel_resp = self.client.post(f'/api/reservas/{reserva_id}/cancelar/')
        self.assertEqual(cancel_resp.status_code, 200)
        # verificar estado
        cancel_data = cancel_resp.data.get('reserva')
        self.assertEqual(cancel_data.get('estado'), 'cancelada')

        # crear otra reserva y confirmar
        create_resp2 = self.client.post('/api/reservas/crear/', {
            'pasajero': self.pasajero.id,
            'vuelo': self.vuelo.id,
            'asiento': self.asiento2.id
        }, format='json')
        self.assertIn(create_resp2.status_code, (200, 201))
        reserva2_id = create_resp2.data.get('id')

        confirm_resp = self.client.post(f'/api/reservas/{reserva2_id}/confirmar/')
        self.assertEqual(confirm_resp.status_code, 200)
        # confirmar que vino boleto en la respuesta
        self.assertIn('boleto', confirm_resp.data)
        boleto = confirm_resp.data['boleto']
        self.assertIn('codigo_barra', boleto)

