# main_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class HomePageView(APIView):
    def get(self, request):
        return Response({"HOME": "home page"})