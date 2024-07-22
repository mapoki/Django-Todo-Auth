from members.serializers import UserRegistrationSerializer, UserLoginSerializer, TaskSerializer
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .utils import generate_access_token, payload
from .models import Task
from jwt.exceptions import ExpiredSignatureError



class UserRegistrationAPIView(APIView):
	serializer_class = UserRegistrationSerializer
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

	def post(self, request):
		try:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid(raise_exception=True):
				new_user = serializer.save()
				if new_user:
					access_token = generate_access_token(new_user)
					data = { 'access_token': access_token }
					response = Response(data, status=status.HTTP_201_CREATED)
					response.set_cookie(key='access_token', value=access_token, httponly=True)
					return response
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		
		except Exception as e:
			print(f"An error occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginAPIView(APIView):
	serializer_class = UserLoginSerializer
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

	def post(self, request):
		try:
			email = request.data.get('email', None)
			user_password = request.data.get('password', None)

			if not user_password:
				raise AuthenticationFailed('A user password is needed.')

			if not email:
				raise AuthenticationFailed('An user email is needed.')

			user_instance = authenticate(request, username=email, password=user_password)

			if not user_instance:
				raise AuthenticationFailed('User not found.')

			if user_instance.is_active:
				user_access_token = generate_access_token(user_instance)
				response = Response()
				response.set_cookie(key='access_token', value=user_access_token, httponly=True)
				response.data = {
					'access_token': user_access_token
				}
				return response

			return Response({
				'message': 'Something went wrong.'
			})
		except Exception as e:
			return Response(f"An error has occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewAPI(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

	def get(self, request):
		try:
			jwt_user = payload(request)

			user_model = get_user_model()
			user = user_model.objects.filter(user_id=jwt_user['user_id']).first()
			user_serializer = UserRegistrationSerializer(user)
			return Response(user_serializer.data)
		
		except ExpiredSignatureError:
			raise AuthenticationFailed("Token has been expired. Please log in again.")
		
		except Exception as e:
			return Response(f"An error has occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserEntryTask(APIView):
	serializer_class = TaskSerializer
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

	def get(self, request):
		try: 
			jwt_user = payload(request)

			task = Task.objects.filter(user_id=jwt_user['user_id'], is_deleted=False)
			serializer = self.serializer_class(task, many=True)
			return Response(serializer.data)
		
		except ExpiredSignatureError:
			raise AuthenticationFailed("Token has been expired. Please log in again.")
			
		except Exception as e:
			return Response(f"An error occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	def post(self, request):
		try:
			jwt_user = payload(request)

			user_id = jwt_user['user_id']
			request.data['user'] = user_id

			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid():
				serializer.save()
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		
		except ExpiredSignatureError:
			raise AuthenticationFailed("Token has been expired. Please log in again.")

		except Exception as e:
			return Response(f"An error occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def put(self, request, pk):
		try:
			jwt_user = payload(request)

			task = Task.objects.get(pk=pk, user_id=jwt_user['user_id'], is_deleted=False)
			request.data['updated_on'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
			request.data['user'] = jwt_user['user_id']
			serializer = self.serializer_class(task, data=request.data)
			if serializer.is_valid():
				serializer.save()
			else:
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		
		except ExpiredSignatureError:
			raise AuthenticationFailed("Token has been expired. Please log in again.")
		
		except Exception as e:
			return Response(f"An error occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
	
	def delete(self, request, pk):
		try:
			jwt_user = payload(request)

			task = Task.objects.get(pk=pk, user_id=jwt_user['user_id'], is_deleted=False)
			task.is_deleted = True
			task.save()
			return Response("Task has been deleted successfully.")

		except ExpiredSignatureError:
			raise AuthenticationFailed("Token has been expired. Please log in again.")

		except Task.DoesNotExist:
			return Response("Task not found or already deleted.")

		except Exception as e:
			return Response(f"An error occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutViewAPI(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

	def get(self, request):
		try: 
			user_token = request.COOKIES.get('access_token', None)
			if user_token:
				response = Response()
				response.delete_cookie('access_token')
				response.data = {
					'message': 'Logged out successfully.'
				}
				return response
			response = Response()
			response.data = {
				'message': 'User is already logged out.'
			}
			return response
		
		except Exception as e:
			return Response(f"An error has occured: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

