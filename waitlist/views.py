from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser


from django.views.decorators.csrf import csrf_exempt


from .serializers import WaitListSerializer
from .models import Waitlist

import logging

logger = logging.getLogger(__name__)

print('waitlisttttttttt')            
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def waitlist_create(request):
    if request.method == 'GET':
        print('hello')
        logger.info('This is the list of waitlist entries')
        waitlist = Waitlist.objects.all()
        logger.info(waitlist)
        serializer = WaitListSerializer(waitlist, many=True)
        logger.info(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = WaitListSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error('Invalid data: %s', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([AllowAny])
def waitlist_delete(request):
    Waitlist.objects.all().delete()
    return Response(status.HTTP_205_RESET_CONTENT)



