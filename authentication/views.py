from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserLoginSerializer
from rest_framework.permissions import IsAuthenticated
import requests

class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'username': user.username,
                'message': 'User registered successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fastapi_url = "http://127.0.0.1:8000/upload"
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        files = {
            'file': (file_obj.name, file_obj.read(), file_obj.content_type)
        }

        try:
            response = requests.post(fastapi_url, files=files, timeout=30)
            response.raise_for_status()  # Raise an error if not 2xx
            return Response(response.json(), status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class QueryDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fastapi_url = "http://127.0.0.1:8000/query"
        question = request.data.get("question")
        if not question:
            return Response({"error": "No question provided"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {"question": question}
        try:
            response = requests.post(fastapi_url, json=payload, timeout=30)
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
