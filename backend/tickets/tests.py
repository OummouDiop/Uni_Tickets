from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User
from .models import TicketRequest, Ticket, PaymentLog

class UserSetup:
    """Helper pour créer des utilisateurs de test"""
    
    @staticmethod
    def create_student(email='student@supnum.mr', password='testpass123'):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name='John',
            last_name='Doe',
            role='STUDENT'
        )
    
    @staticmethod
    def create_admin(email='admin@supnum.mr', password='adminpass123'):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
    
    @staticmethod
    def create_agent(email='agent@supnum.mr', password='agentpass123'):
        return User.objects.create_user(
            email=email,
            password=password,
            first_name='Agent',
            last_name='Restaurant',
            role='AGENT'
        )

class TicketRequestModelTest(TestCase):
    """Tests pour le modèle TicketRequest"""
    
    def setUp(self):
        self.student = UserSetup.create_student()
    
    def test_create_ticket_request(self):
        """Test création d'une demande de ticket"""
        start = timezone.now().date() + timedelta(days=1)
        end = start + timedelta(days=5)
        
        request = TicketRequest.objects.create(
            student=self.student,
            start_date=start,
            end_date=end,
            status='PENDING'
        )
        
        self.assertEqual(request.number_of_days, 6)
        self.assertEqual(request.total_amount, 30.00)
    
    def test_ticket_amount_calculation(self):
        """Test le calcul du montant"""
        start = timezone.now().date() + timedelta(days=1)
        end = start + timedelta(days=9)  # 10 jours
        
        request = TicketRequest.objects.create(
            student=self.student,
            start_date=start,
            end_date=end
        )
        
        self.assertEqual(request.total_amount, 50.00)  # 10 * 5

class TicketModelTest(TestCase):
    """Tests pour le modèle Ticket"""
    
    def setUp(self):
        self.student = UserSetup.create_student()
        start = timezone.now().date() + timedelta(days=1)
        self.request = TicketRequest.objects.create(
            student=self.student,
            start_date=start,
            end_date=start + timedelta(days=2)
        )
    
    def test_create_ticket_generates_qr_token(self):
        """Test que la création génère un QR token unique"""
        ticket = Ticket.objects.create(
            request=self.request,
            date=timezone.now().date()
        )
        
        self.assertIsNotNone(ticket.qr_token)
        self.assertEqual(len(ticket.qr_token), 36)  # UUID4 length
    
    def test_qr_token_is_unique(self):
        """Test que chaque ticket a un QR token unique"""
        ticket1 = Ticket.objects.create(
            request=self.request,
            date=timezone.now().date()
        )
        ticket2 = Ticket.objects.create(
            request=self.request,
            date=timezone.now().date() + timedelta(days=1)
        )
        
        self.assertNotEqual(ticket1.qr_token, ticket2.qr_token)
