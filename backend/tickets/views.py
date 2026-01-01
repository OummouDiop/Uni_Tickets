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

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'ADMIN'

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
            raise serializers.ValidationError("Only students can create requests")
        start = serializer.validated_data['start_date']
        end = serializer.validated_data['end_date']
        if start >= end:
            raise serializers.ValidationError("End date must be after start date")
        # Check no overlapping dates
        existing = TicketRequest.objects.filter(
            student=self.request.user,
            status__in=['PENDING', 'PAID', 'APPROVED'],
            start_date__lte=end,
            end_date__gte=start
        )
        if existing.exists():
            raise serializers.ValidationError("Overlapping request dates")
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        ticket_request = self.get_object()
        ticket_request.status = 'APPROVED'
        ticket_request.approved_at = timezone.now()
        ticket_request.save()
        # Create tickets
        current_date = ticket_request.start_date
        while current_date <= ticket_request.end_date:
            Ticket.objects.create(
                request=ticket_request,
                date=current_date
            )
            current_date += timedelta(days=1)
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        ticket_request = self.get_object()
        ticket_request.status = 'REJECTED'
        ticket_request.rejected_at = timezone.now()
        ticket_request.save()
        return Response({'status': 'rejected'})

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

    @action(detail=True, methods=['post'], permission_classes=[IsAgent])
    def scan(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == 'USED':
            return Response({'valid': False, 'message': 'Already used'})
        if ticket.date < timezone.now().date():
            ticket.status = 'EXPIRED'
            ticket.save()
            return Response({'valid': False, 'message': 'Expired'})
        ticket.status = 'USED'
        ticket.used_at = timezone.now()
        ticket.scanned_by = request.user
        ticket.save()
        return Response({'valid': True, 'message': 'Valid'})
