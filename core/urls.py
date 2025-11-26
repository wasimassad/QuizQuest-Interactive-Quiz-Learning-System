from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

    # quizzes
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('quizzes/<int:quiz_id>/take/', views.take_quiz_view, name='take_quiz'),
]
