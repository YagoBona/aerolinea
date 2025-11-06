from rest_framework.decorators import action
from rest_framework.response import Response


from rest_framework import viewsets, permissions, filters
from vuelos.models import Avion, Vuelo, Pasajero, Asiento, Reserva, Boleto
from .serializers import AvionSerializer, VueloSerializer, PasajeroSerializer, AsientoSerializer, ReservaSerializer, BoletoSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_staff or getattr(request.user, 'rol', None) == 'admin'

class AvionViewSet(viewsets.ModelViewSet):
	queryset = Avion.objects.all()
	serializer_class = AvionSerializer
	permission_classes = [IsAdminOrReadOnly]

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

class PasajeroViewSet(viewsets.ModelViewSet):
	queryset = Pasajero.objects.all()
	serializer_class = PasajeroSerializer
	permission_classes = [permissions.IsAuthenticated]

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

class BoletoViewSet(viewsets.ModelViewSet):
	queryset = Boleto.objects.all()
	serializer_class = BoletoSerializer
	permission_classes = [permissions.IsAuthenticated]
