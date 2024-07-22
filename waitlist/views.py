from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


from django.views.decorators.csrf import csrf_exempt


from .serializers import WaitlistSerializer
from .models import Waitlist

@api_view(['POST', 'GET'])
@csrf_exempt
@permission_classes([AllowAny])

def waitlist_create(request):
    if request.method == 'GET':
        waitlist = Waitlist.objects.all()
        serializer = WaitlistSerializer(waitlist, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
        return Response(serializer.data, status.HTTP_201_CREATED)
            
