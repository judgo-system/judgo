import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Response


def add_highlight(request, responseId):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        response = get_object_or_404(Response, id=responseId)

        if request.method == 'PUT':
            data = json.load(request)
            highlights = data.get('highlight')
            response.highlight = highlights
            # response.highlight = '|||'.join(tag for tag in set(highlights.split("|||")))
            
            response.save()

            return JsonResponse({'status': 'highlight updated!'})

    return HttpResponseBadRequest('Invalid request')

def remove_highlight(request, responseId):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        response = get_object_or_404(Response, id=responseId)

        if request.method == 'PUT':
            data = json.load(request)
            deleted_value = data.get('payload')
            highlight = response.highlight.split(",")
            highlight.remove(deleted_value['highlight'])
            
            if highlight:
                response.highlight = ",".join(highlight) 
            else:
                response.highlight = None
            
            response.save()

            return JsonResponse({'status': 'highlight remove!'})

    return HttpResponseBadRequest('Invalid request')