from django.contrib import admin
from .models import TicketRequest, Ticket, PaymentLog

@admin.register(TicketRequest)
class TicketRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_name', 'start_date', 'end_date', 'number_of_days', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name')
    readonly_fields = ('number_of_days', 'total_amount', 'created_at', 'approved_at', 'rejected_at')
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Request Details', {
            'fields': ('start_date', 'end_date', 'number_of_days', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_reference', 'payment_screenshot')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'approved_at', 'rejected_at')
        }),
    )

    def student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_name.short_description = 'Student'

    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        updated = 0
        for ticket_request in queryset.filter(status__in=['PENDING', 'PAID']):
            ticket_request.status = 'APPROVED'
            ticket_request.approved_at = timezone.now()
            ticket_request.save()
            
            # Create tickets
            current_date = ticket_request.start_date
            while current_date <= ticket_request.end_date:
                Ticket.objects.get_or_create(
                    request=ticket_request,
                    date=current_date
                )
                current_date += timedelta(days=1)
            updated += 1
        
        self.message_user(request, f'{updated} requests approved and tickets created.')
    approve_requests.short_description = 'Approve selected requests'

    def reject_requests(self, request, queryset):
        from django.utils import timezone
        
        updated = queryset.filter(status__in=['PENDING', 'PAID']).update(
            status='REJECTED',
            rejected_at=timezone.now()
        )
        self.message_user(request, f'{updated} requests rejected.')
    reject_requests.short_description = 'Reject selected requests'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('qr_token', 'student_name', 'date', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('request__student__email', 'request__student__first_name', 'qr_token')
    readonly_fields = ('qr_token', 'created_at', 'used_at', 'scanned_by')
    fieldsets = (
        ('Ticket Information', {
            'fields': ('request', 'date', 'qr_token', 'status')
        }),
        ('Usage Information', {
            'fields': ('used_at', 'scanned_by', 'created_at')
        }),
    )

    def student_name(self, obj):
        return f"{obj.request.student.first_name} {obj.request.student.last_name}"
    student_name.short_description = 'Student'

@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('reference', 'student_name', 'status', 'ticket_request_amount', 'verified_at', 'created_at')
    list_filter = ('status', 'created_at', 'verified_at')
    search_fields = ('reference', 'ticket_request__student__email', 'ticket_request__student__first_name')
    readonly_fields = ('created_at', 'verified_at', 'verified_by')
    fieldsets = (
        ('Payment Information', {
            'fields': ('ticket_request', 'reference', 'screenshot')
        }),
        ('Verification', {
            'fields': ('status', 'verified_by', 'verified_at', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def student_name(self, obj):
        return f"{obj.ticket_request.student.first_name} {obj.ticket_request.student.last_name}"
    student_name.short_description = 'Student'

    def ticket_request_amount(self, obj):
        return f"{obj.ticket_request.total_amount} MRU"
    ticket_request_amount.short_description = 'Amount'

    actions = ['mark_as_verified', 'mark_as_failed']

    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        
        updated = queryset.filter(status='PENDING').update(
            status='VERIFIED',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} payments marked as verified.')
    mark_as_verified.short_description = 'Mark selected as verified'

    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='FAILED')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_as_failed.short_description = 'Mark selected as failed'
