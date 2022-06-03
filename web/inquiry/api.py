from rest_framework import viewsets
from .serializers import InquirySerializer
from .models import Inquiry


class InquiryAPIView(viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    queryset = Inquiry.objects.all()

    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)