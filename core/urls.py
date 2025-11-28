from django.urls import path
from . import views

urlpatterns = [
    # public / auth
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # quizzes
    path("quizzes/", views.quiz_list_view, name="quiz_list"),
    path("quiz/<int:quiz_id>/", views.take_quiz_view, name="take_quiz"),

    # optional separate admin dashboard (you can keep or remove)
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
]
