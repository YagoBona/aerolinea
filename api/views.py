from rest_framework.decorators import action
from rest_framework.response import Response


from rest_framework import viewsets, permissions, filters, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404

from vuelos.models import Avion, Vuelo, Pasajero, Asiento, Reserva, Boleto
from .serializers import (
	AvionSerializer,
	VueloSerializer,
	PasajeroSerializer,
	AsientoSerializer,
	ReservaSerializer,
	ReservaCreateSerializer,
	BoletoSerializer,
)

from .services.reserva_service import crear_reserva
from .services.boleto_service import generar_boleto_desde_reserva


class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'


class AvionViewSet(viewsets.ModelViewSet):
	queryset = Avion.objects.all()
	serializer_class = AvionSerializer
	permission_classes = [IsAdminOrReadOnly]

	@action(detail=True, methods=['get'], url_path='layout')
	def layout(self, request, pk=None):
		avion = self.get_object()
		asientos = avion.asiento_set.all().values('id', 'fila', 'columna', 'numero')
		return Response(list(asientos))


class VueloViewSet(viewsets.ModelViewSet):
	queryset = Vuelo.objects.all()
	serializer_class = VueloSerializer
	permission_classes = [IsAdminOrReadOnly]
	filter_backends = [filters.SearchFilter]
	search_fields = ['origen', 'destino', 'fecha_salida']

	def get_queryset(self):
		queryset = Vuelo.objects.all()
		origen = self.request.query_params.get('origen')
		destino = self.request.query_params.get('destino')
		fecha = self.request.query_params.get('fecha')
		if origen:
			queryset = queryset.filter(origen__icontains=origen)
		if destino:
			queryset = queryset.filter(destino__icontains=destino)
		if fecha:
			queryset = queryset.filter(fecha_salida__date=fecha)
		return queryset

	@action(detail=True, methods=['get'], url_path='pasajeros')
	def pasajeros_por_vuelo(self, request, pk=None):
		vuelo = self.get_object()
		reservas = vuelo.reserva_set.select_related('pasajero')
		pasajeros = [r.pasajero for r in reservas]
		serializer = PasajeroSerializer(pasajeros, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['get'], url_path=r'asiento/(?P<asiento_id>[^/.]+)/disponible')
	def asiento_disponible(self, request, pk=None, asiento_id=None):
		vuelo = self.get_object()
		ocupada = Reserva.objects.filter(
			vuelo=vuelo, asiento_id=asiento_id, estado__in=['confirmada', 'pendiente']
		).exists()
		return Response({'disponible': not ocupada})


class PasajeroViewSet(viewsets.ModelViewSet):
	queryset = Pasajero.objects.all()
	serializer_class = PasajeroSerializer

	def get_permissions(self):
		if self.action == 'create':
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated()]

	@action(detail=True, methods=['get'], url_path='reservas-activas')
	def reservas_activas(self, request, pk=None):
		pasajero = self.get_object()
		reservas = pasajero.reserva_set.filter(estado='confirmada')
		serializer = ReservaSerializer(reservas, many=True)
		return Response(serializer.data)


class AsientoViewSet(viewsets.ModelViewSet):
	queryset = Asiento.objects.all()
	serializer_class = AsientoSerializer
	permission_classes = [IsAdminOrReadOnly]


class ReservaViewSet(viewsets.ModelViewSet):
	queryset = Reserva.objects.all()
	serializer_class = ReservaSerializer
	permission_classes = [permissions.IsAuthenticated]

	@action(detail=False, methods=['post'], url_path='crear')
	def crear(self, request):
		# payload: {"pasajero": <id>, "vuelo": <id>, "asiento": <id>}
		pasajero_id = request.data.get('pasajero')
		vuelo_id = request.data.get('vuelo')
		asiento_id = request.data.get('asiento')
		if not pasajero_id or not vuelo_id or not asiento_id:
			return Response({'detail': 'pasajero, vuelo y asiento son requeridos'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			reserva = crear_reserva(pasajero_id, vuelo_id, asiento_id)
		except ValidationError as e:
			# e.detail may be a list/dict
			detail = e.detail if hasattr(e, 'detail') else str(e)
			return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
		serializer = ReservaSerializer(reserva)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['post'], url_path='confirmar')
	def confirmar(self, request, pk=None):
		reserva = self.get_object()
		owner_user = getattr(reserva.pasajero, 'usuario', None)
		if request.user != owner_user and not request.user.is_staff:
			raise PermissionDenied("No tiene permisos para confirmar esta reserva")
		if reserva.estado == 'confirmada':
			return Response({'detail': 'Reserva ya confirmada'}, status=status.HTTP_400_BAD_REQUEST)
		reserva.estado = 'confirmada'
		reserva.save()
		try:
			boleto = generar_boleto_desde_reserva(reserva.id)
		except ValidationError as e:
			detail = e.detail if hasattr(e, 'detail') else str(e)
			return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
		boleto_serializer = BoletoSerializer(boleto)
		return Response({'reserva': ReservaSerializer(reserva).data, 'boleto': boleto_serializer.data})

	@action(detail=True, methods=['post'], url_path='cancelar')
	def cancelar(self, request, pk=None):
		reserva = self.get_object()
		owner_user = getattr(reserva.pasajero, 'usuario', None)
		if request.user != owner_user and not request.user.is_staff:
			raise PermissionDenied("No tiene permisos para cancelar esta reserva")
		if reserva.estado == 'cancelada':
			return Response({'detail': 'Reserva ya cancelada'}, status=status.HTTP_400_BAD_REQUEST)
		reserva.estado = 'cancelada'
		reserva.save()
		return Response({'reserva': ReservaSerializer(reserva).data})


class BoletoViewSet(viewsets.ModelViewSet):
	queryset = Boleto.objects.all()
	serializer_class = BoletoSerializer
	permission_classes = [permissions.IsAuthenticated]
