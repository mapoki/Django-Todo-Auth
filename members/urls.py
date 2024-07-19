from django.urls import path
from members.views import (
	UserRegistrationAPIView,
	UserLoginAPIView,
	UserViewAPI,
	UserLogoutViewAPI,
    UserEntryTask
)


urlpatterns = [
	path('user/register/', UserRegistrationAPIView.as_view()),
	path('user/login/', UserLoginAPIView.as_view()),
	path('user/', UserViewAPI.as_view()),
	path('user/logout/', UserLogoutViewAPI.as_view()),
    
	path('user/tasks/view/', UserEntryTask.as_view(), name='view_user_task'),
	path('user/tasks/add/', UserEntryTask.as_view(), name='add_user_task'),
]
