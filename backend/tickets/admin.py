from django.contrib import admin
from .models import TicketRequest, Ticket

@admin.register(TicketRequest)
class TicketRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'start_date', 'end_date', 'status', 'total_amount')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('student__email', 'student__first_name', 'student__last_name')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('request', 'date', 'status', 'qr_token')
    list_filter = ('status', 'date')
    search_fields = ('request__student__email', 'qr_token')
