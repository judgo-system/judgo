import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from core.models import Task


def add_tag(request, inquiryId):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        inquiry = get_object_or_404(Task, id=inquiryId)

        if request.method == 'PUT':
            data = json.load(request)
            updated_values = data.get('payload')
            
            if inquiry.tags:
                tag_set = set(inquiry.tags.split(","))
                tag_set.add(updated_values['tags'])
                inquiry.tags = ','.join(tag for tag in tag_set)
            else:
                inquiry.tags = updated_values['tags'] 
            
            inquiry.save()

            return JsonResponse({'status': 'Tags updated!'})

    return HttpResponseBadRequest('Invalid request')

def remove_tag(request, inquiryId):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        inquiry = get_object_or_404(Task, id=inquiryId)

        if request.method == 'PUT':
            data = json.load(request)
            deleted_value = data.get('payload')
            tags = inquiry.tags.split(",")
            tags.remove(deleted_value['tags'])
            
            if tags:
                inquiry.tags = ",".join(tags) 
            else:
                inquiry.tags = None
            
            inquiry.save()

            return JsonResponse({'status': 'Tags remove!'})

    return HttpResponseBadRequest('Invalid request')

# from rest_framework import viewsets
# from .serializers import InquirySerializer
# from .models import Inquiry


# class InquiryAPIView(viewsets.ModelViewSet):
#     serializer_class = InquirySerializer
#     queryset = Inquiry.objects.all()

    
#     def update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return super().update(request, *args, **kwargs)