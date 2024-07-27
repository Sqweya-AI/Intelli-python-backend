from auth_app.views import CsrfExemptSessionAuthentication
from .serializers import BillingModelSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from .models import BillingModel

class BillingViewSet(viewsets.ModelViewSet):
    queryset = BillingModel.objects.all()
    serializer_class = BillingModelSerializer
    authentication_classes = [CsrfExemptSessionAuthentication] # to disable csrf check
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        # if not request.user.is_authenticated:
            # return Response({'error': 'User is not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.role == 'manager':
            return Response({'error': 'User is not a manager'}, status=status.HTTP_403_FORBIDDEN)
        card_number = str(request.data.get('card_number'))
        cvv = str(request.data.get('cvv'))
        return Response({'Subscription Status': 'Success', 'Billing-Info': {"Card NO:": card_number, "CVV":cvv}}, status=status.HTTP_200_OK)