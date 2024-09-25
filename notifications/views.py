# from django.shortcuts import render
# import queue
# from django.http import StreamingHttpResponse

# # Create your views here.

# # Global queue to store messages
# event_queue = queue.Queue()

# def event_stream():
#     while True:
#         message = event_queue.get()  # Block until a message is available
#         yield message


# def sse_view(request):
#     response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
#     response['Cache-Control'] = 'no-cache'
#     return response


from django.shortcuts import get_object_or_404
from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

# from .models import Notification
# from .serializers import NotificationSerializer
from appservice.models import AppService, ChatSession
from appservice.serializers import ChatSessionNotificationSerializer



@api_view(['GET'])
@csrf_exempt
def notifications(request, phone_number):
    appservice  = get_object_or_404(AppService, phone_number=phone_number)
    if appservice:
        notifications  = ChatSession.objects.filter(
            appservice=appservice
            ).annotate(
                notification_count=Count('notifications')
            ).filter(
                notification_count__gt=0
                ).prefetch_related('notifications')
        
        serializer     = ChatSessionNotificationSerializer(notifications, many=True)

        return Response(serializer.data, status=200)


