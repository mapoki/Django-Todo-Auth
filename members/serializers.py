from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, User


class UserRegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	class Meta:
		model = get_user_model()
		fields = ['email', 'username', 'password']

	def create(self, validated_data):
		user_password = validated_data.get('password', None)
		db_instance = self.Meta.model(email=validated_data.get('email'), username=validated_data.get('username'))
		db_instance.set_password(user_password)
		db_instance.save()
		return db_instance



class UserLoginSerializer(serializers.Serializer):
	email = serializers.CharField(max_length=100)
	username = serializers.CharField(max_length=100, read_only=True)
	password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	token = serializers.CharField(max_length=255, read_only=True)



class TaskSerializer(serializers.ModelSerializer):
	title = serializers.CharField(max_length=255)

	class Meta:
		model = Task
		fields = ('title',)

		def create(self, validated_data):
			user_id = validated_data.pop('user_id')  # Extract user_id from validated data
			task = Task.objects.create(user_id=user_id, **validated_data)
			return task
