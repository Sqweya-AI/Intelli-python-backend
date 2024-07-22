from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import IntelliWaitList
from .serializers import IntelliWaitListSerializer



# Create your views here.
import logging

logger = logging.getLogger(__name__)

@api_view(['GET','POST'])
@permission_classes([AllowAny,])
def waitlist_create(request):
    if request.method == 'GET':
        logger.info('This is the list of waitlist entries')
        waitlist = IntelliWaitList.objects.all()
        logger.info(waitlist)
        serializer = IntelliWaitListSerializer(waitlist, many=True)
        logger.info(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = IntelliWaitListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error('Invalid data: %s', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)