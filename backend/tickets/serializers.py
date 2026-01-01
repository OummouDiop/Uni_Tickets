from rest_framework import serializers
from .models import TicketRequest, Ticket
import qrcode
import base64
from io import BytesIO

class TicketRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = TicketRequest
        fields = '__all__'
        read_only_fields = ('student', 'number_of_days', 'total_amount', 'created_at', 'approved_at', 'rejected_at')

class TicketSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()

    def get_qr_code(self, obj):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(obj.qr_token)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('qr_token', 'created_at', 'used_at', 'scanned_by')