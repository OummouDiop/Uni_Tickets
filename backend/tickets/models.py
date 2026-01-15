from django.db import models
from accounts.models import User
import uuid
from datetime import timedelta

class TicketRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_days = models.PositiveIntegerField(editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_screenshot = models.ImageField(upload_to='payments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.number_of_days = (self.end_date - self.start_date).days + 1
            self.total_amount = self.number_of_days * 5  # 5 MRU per day
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Request by {self.student} from {self.start_date} to {self.end_date}"

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('VALID', 'Valid'),
        ('USED', 'Used'),
        ('EXPIRED', 'Expired'),
    )

    request = models.ForeignKey(TicketRequest, on_delete=models.CASCADE, related_name='tickets')
    date = models.DateField()
    qr_token = models.CharField(max_length=100, unique=True, editable=False, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='VALID')
    used_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scanned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'date')
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket for {self.request.student} on {self.date}"

class PaymentLog(models.Model):
    """Modèle pour tracker les paiements"""
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('FAILED', 'Failed'),
    )

    ticket_request = models.OneToOneField(TicketRequest, on_delete=models.CASCADE, related_name='payment_log')
    reference = models.CharField(max_length=100, unique=True)
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
