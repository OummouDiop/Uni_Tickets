from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import timedelta, datetime
from .models import PaymentLog, TicketRequest, Ticket
from .serializers import PaymentLogSerializer
from .permissions import IsAdmin

class PaymentLogViewSet(viewsets.ModelViewSet):
    """Admin viewset pour gérer les logs de paiement"""
    serializer_class = PaymentLogSerializer
    permission_classes = [IsAdmin]
    queryset = PaymentLog.objects.all()

    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Obtenir tous les paiements en attente de vérification"""
        pending = PaymentLog.objects.filter(status='PENDING')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def verified_payments(self, request):
        """Obtenir tous les paiements vérifiés"""
        verified = PaymentLog.objects.filter(status='VERIFIED')
        serializer = self.get_serializer(verified, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Vérifier un paiement"""
        payment = self.get_object()
        if payment.status != 'PENDING':
            return Response(
                {'error': 'Payment is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'VERIFIED'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.save()
        
        # Mettre à jour la demande de tickets
        ticket_request = payment.ticket_request
        ticket_request.status = 'PAID'
        ticket_request.save()
        
        return Response({
            'status': 'verified',
            'message': 'Payment verified and request marked as paid'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un paiement"""
        payment = self.get_object()
        if payment.status != 'PENDING':
            return Response(
                {'error': 'Payment is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'FAILED'
        payment.verified_by = request.user
        payment.verified_at = timezone.now()
        payment.save()
        
        return Response({'status': 'rejected'})

class AdminDashboardViewSet(viewsets.ViewSet):
    """Viewset pour le dashboard admin"""
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Obtenir un aperçu général du système"""
        today = timezone.now().date()
        
        overview = {
            'total_students': TicketRequest.objects.values('student').distinct().count(),
            'pending_requests': TicketRequest.objects.filter(status='PENDING').count(),
            'approved_requests': TicketRequest.objects.filter(status='APPROVED').count(),
            'today_requests': TicketRequest.objects.filter(created_at__date=today).count(),
            'pending_payments': PaymentLog.objects.filter(status='PENDING').count(),
            'verified_payments': PaymentLog.objects.filter(status='VERIFIED').count(),
            'today_revenue': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date=today
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'today_tickets_used': Ticket.objects.filter(
                status='USED',
                used_at__date=today
            ).count(),
            'today_tickets_valid': Ticket.objects.filter(
                status='VALID',
                date=today
            ).count(),
        }
        
        return Response(overview)

    @action(detail=False, methods=['get'])
    def weekly_statistics(self, request):
        """Obtenir les statistiques hebdomadaires"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        stats = {
            'week_start': week_start.isoformat(),
            'week_end': (week_start + timedelta(days=6)).isoformat(),
            'total_requests': TicketRequest.objects.filter(
                created_at__date__range=[week_start, week_start + timedelta(days=6)]
            ).count(),
            'approved_requests': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__range=[week_start, week_start + timedelta(days=6)]
            ).count(),
            'total_revenue': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__range=[week_start, week_start + timedelta(days=6)]
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'tickets_used': Ticket.objects.filter(
                status='USED',
                used_at__date__range=[week_start, week_start + timedelta(days=6)]
            ).count(),
            'tickets_expired': Ticket.objects.filter(
                status='EXPIRED',
                date__range=[week_start, week_start + timedelta(days=6)]
            ).count(),
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def monthly_statistics(self, request):
        """Obtenir les statistiques mensuelles"""
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        stats = {
            'month': month_start.strftime('%Y-%m'),
            'total_requests': TicketRequest.objects.filter(
                created_at__date__gte=month_start
            ).count(),
            'approved_requests': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__gte=month_start
            ).count(),
            'total_revenue': TicketRequest.objects.filter(
                status='APPROVED',
                created_at__date__gte=month_start
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'tickets_used': Ticket.objects.filter(
                status='USED',
                used_at__date__gte=month_start
            ).count(),
            'active_students': TicketRequest.objects.filter(
                created_at__date__gte=month_start
            ).values('student').distinct().count(),
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def users_management(self, request):
        """Obtenir la liste des utilisateurs pour la gestion"""
        from accounts.models import User
        
        role = request.query_params.get('role')
        
        if role:
            users = User.objects.filter(role=role).values(
                'id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined'
            )
        else:
            users = User.objects.values(
                'id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined'
            )
        
        return Response(list(users))

    @action(detail=False, methods=['post'])
    def deactivate_user(self, request):
        """Désactiver un utilisateur"""
        from accounts.models import User
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return Response({'message': 'User deactivated successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def activate_user(self, request):
        """Activer un utilisateur"""
        from accounts.models import User
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({'message': 'User activated successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
