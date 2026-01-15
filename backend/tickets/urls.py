from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import admin_views
from . import admin_dashboard

router = DefaultRouter()
router.register(r'requests', views.TicketRequestViewSet, basename='ticket-request')
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'admin/requests', admin_views.AdminTicketRequestViewSet, basename='admin-ticket-request')
router.register(r'admin/tickets', admin_views.AdminTicketViewSet, basename='admin-ticket')
router.register(r'admin/payments', admin_dashboard.PaymentLogViewSet, basename='admin-payment')
router.register(r'admin/dashboard', admin_dashboard.AdminDashboardViewSet, basename='admin-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]