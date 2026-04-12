from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # AUTH
    path('', views.home),
    path('login/', views.login_view),
    path('register/', views.register),
    path('logout/', views.logout),
    path('forgot-password/', views.forgot_password),

    # DASHBOARD
    path('dashboard/', views.dashboard),

    # CRUD
    path('electricians/', views.electricians),
    path('delete-electrician/<int:id>/', views.delete_electrician),

    path('jobs/', views.jobs),
    path('delete-job/<int:id>/', views.delete_job),

    path('tasks/', views.tasks),
    path('delete-task/<int:id>/', views.delete_task),

    path('materials/', views.materials),
    path('delete-material/<int:id>/', views.delete_material),

    # OTHER
    path('reports/', views.reports),
    path('profile/', views.profile),
]