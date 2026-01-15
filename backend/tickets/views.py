from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import TicketRequest, Ticket
from .serializers import TicketRequestSerializer, TicketSerializer

class IsStudent(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'STUDENT'

class IsAgent(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'AGENT'

class TicketRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TicketRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = TicketRequest.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return TicketRequest.objects.filter(student=user)
        elif user.role in ['ADMIN', 'AGENT']:
            return TicketRequest.objects.all()
        return TicketRequest.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'STUDENT':
            raise ValueError("Only students can create requests")
        start = serializer.validated_data['start_date']
        end = serializer.validated_data['end_date']
        if start >= end:
            raise ValueError("End date must be after start date")
        # Check no overlapping dates
        existing = TicketRequest.objects.filter(
            student=self.request.user,
            status__in=['PENDING', 'PAID', 'APPROVED'],
            start_date__lte=end,
            end_date__gte=start
        )
        if existing.exists():
            raise ValueError("Overlapping request dates")
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_requests(self, request):
        """Obtenir mes demandes"""
        requests = TicketRequest.objects.filter(student=request.user)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def statistics(self, request):
        """Obtenir mes statistiques de tickets"""
        requests = TicketRequest.objects.filter(student=request.user)
        tickets = Ticket.objects.filter(request__student=request.user)
        
        stats = {
            'total_requests': requests.count(),
            'approved_requests': requests.filter(status='APPROVED').count(),
            'rejected_requests': requests.filter(status='REJECTED').count(),
            'valid_tickets': tickets.filter(status='VALID').count(),
            'used_tickets': tickets.filter(status='USED').count(),
            'expired_tickets': tickets.filter(status='EXPIRED').count(),
            'total_spent': sum([r.total_amount for r in requests.filter(status='APPROVED')])
        }
        
        return Response(stats)

class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return Ticket.objects.filter(request__student=user)
        elif user.role in ['ADMIN', 'AGENT']:
            return Ticket.objects.all()
        return Ticket.objects.none()

    @action(detail=False, methods=['get'], permission_classes=[IsStudent])
    def my_tickets(self, request):
        """Obtenir mes tickets"""
        tickets = Ticket.objects.filter(request__student=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAgent])
    def scan(self, request, pk=None):
        """Scanner un ticket et le marquer comme utilisé"""
        ticket = self.get_object()
        
        if ticket.status == 'USED':
            return Response({
                'valid': False,
                'message': 'Already used',
                'status': ticket.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if ticket.date < timezone.now().date():
            ticket.status = 'EXPIRED'
            ticket.save()
            return Response({
                'valid': False,
                'message': 'Expired',
                'status': ticket.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.status = 'USED'
        ticket.used_at = timezone.now()
        ticket.scanned_by = request.user
        ticket.save()
        
        return Response({
            'valid': True,
            'message': 'Valid',
            'status': ticket.status,
            'student': f"{ticket.request.student.first_name} {ticket.request.student.last_name}",
            'used_at': ticket.used_at
        })
