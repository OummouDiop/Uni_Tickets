from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import timedelta, datetime
from .models import TicketRequest, Ticket
from .serializers import TicketRequestSerializer, TicketSerializer

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'ADMIN'

class AdminTicketRequestViewSet(viewsets.ModelViewSet):
    """Admin views pour gérer les demandes de tickets"""
    serializer_class = TicketRequestSerializer
    permission_classes = [IsAdmin]
    queryset = TicketRequest.objects.all()

    @action(detail=False, methods=['get'])
    def pending_requests(self, request):
        """Obtenir toutes les demandes en attente de validation"""
        pending = TicketRequest.objects.filter(status='PENDING')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def paid_requests(self, request):
        """Obtenir toutes les demandes payées"""
        paid = TicketRequest.objects.filter(status='PAID')
        serializer = self.get_serializer(paid, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver une demande de tickets"""
        ticket_request = self.get_object()
        if ticket_request.status not in ['PENDING', 'PAID']:
            return Response(
                {'error': 'Can only approve pending or paid requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket_request.status = 'APPROVED'
        ticket_request.approved_at = timezone.now()
        ticket_request.save()
        
        # Créer les tickets individuels
        from datetime import timedelta
        current_date = ticket_request.start_date
        while current_date <= ticket_request.end_date:
            Ticket.objects.get_or_create(
                request=ticket_request,
                date=current_date
            )
            current_date += timedelta(days=1)
        
        return Response({
            'status': 'approved',
            'message': f'Request approved and {ticket_request.number_of_days} tickets created'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter une demande de tickets"""
        ticket_request = self.get_object()
        if ticket_request.status not in ['PENDING', 'PAID']:
            return Response(
                {'error': 'Can only reject pending or paid requests'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket_request.status = 'REJECTED'
        ticket_request.rejected_at = timezone.now()
        ticket_request.save()
        
        return Response({'status': 'rejected'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtenir les statistiques globales des tickets"""
        today = timezone.now().date()
        
        # Statistiques par période
        period = request.query_params.get('period', 'day')  # day, week, month
        
        if period == 'day':
            start_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
        elif period == 'month':
            start_date = today.replace(day=1)
        else:
            start_date = today
        
        stats = {
            'total_requests': TicketRequest.objects.filter(
                created_at__date__gte=start_date
            ).count(),
            'approved_requests': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__gte=start_date
            ).count(),
            'rejected_requests': TicketRequest.objects.filter(
                status='REJECTED',
                created_at__date__gte=start_date
            ).count(),
            'total_revenue': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__gte=start_date
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'tickets_used': Ticket.objects.filter(
                status='USED',
                used_at__date__gte=start_date
            ).count(),
            'tickets_valid': Ticket.objects.filter(
                status='VALID',
                date__gte=start_date
            ).count(),
            'tickets_expired': Ticket.objects.filter(
                status='EXPIRED',
                date__lt=today
            ).count(),
            'period': period,
            'start_date': start_date.isoformat()
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def student_statistics(self, request):
        """Obtenir les statistiques par étudiant"""
        students = TicketRequest.objects.values('student').annotate(
            total_requests=Count('id'),
            total_amount=Sum('total_amount'),
            approved=Count('id', filter=Q(status='APPROVED')),
            rejected=Count('id', filter=Q(status='REJECTED'))
        ).order_by('-total_requests')
        
        return Response(students)

    @action(detail=False, methods=['get'])
    def daily_revenue(self, request):
        """Obtenir le revenu journalier"""
        days = request.query_params.get('days', '30')
        try:
            days = int(days)
        except:
            days = 30
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        revenue_data = TicketRequest.objects.filter(
            status='APPROVED',
            created_at__date__gte=start_date
        ).values('created_at__date').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__date')
        
        return Response(revenue_data)

class AdminTicketViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin views pour consulter les tickets"""
    serializer_class = TicketSerializer
    permission_classes = [IsAdmin]
    queryset = Ticket.objects.all()

    @action(detail=False, methods=['get'])
    def today_tickets(self, request):
        """Obtenir les tickets du jour"""
        today = timezone.now().date()
        tickets = Ticket.objects.filter(date=today)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def used_today(self, request):
        """Obtenir les tickets utilisés aujourd'hui"""
        today = timezone.now().date()
        tickets = Ticket.objects.filter(
            date=today,
            status='USED'
        )
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Obtenir les tickets par plage de dates"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()
        except:
            return Response(
                {'error': 'Invalid date format (use YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tickets = Ticket.objects.filter(date__range=[start, end])
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Obtenir tous les tickets d'un étudiant"""
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tickets = Ticket.objects.filter(request__student_id=student_id)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
