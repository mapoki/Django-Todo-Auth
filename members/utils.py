import jwt
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.exceptions import AuthenticationFailed


def generate_access_token(user):
	payload = {
		'user_id': user.user_id,
		'exp': datetime.utcnow() + timedelta(minutes=5), 
		'iat': datetime.utcnow(),
	}

	access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
	return access_token


def payload(request):
	user_token = request.COOKIES.get('access_token')

	if not user_token:
		raise AuthenticationFailed('Unauthenticated user.')

	payload = jwt.decode(user_token, settings.SECRET_KEY, algorithms=['HS256'])
	return payload

