from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from social_django.utils import psa
from django.contrib.auth import login
from oauth.serializers import SocialSerializer


class SocialLoginView(APIView):
    permission_classes = []
    serializer_class = SocialSerializer

    @psa('social:complete')
    def post(self, request, backend):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response(
                {'error': 'Access token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = request.backend.do_auth(access_token)
            if user:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.name,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Authentication failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
