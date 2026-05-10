from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ================= AUTH =================
    path('', views.home),
    path('login/', views.login_view),
    path('register/', views.register),
    path('logout/', views.logout),
    path('forgot-password/', views.forgot_password),

    # ================= DASHBOARD =================
    path('dashboard/', views.dashboard),
    
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    
    path('upload-job/', views.upload_job, name='upload_job'),
    path('upload-report/', views.upload_report, name='upload_report'),


    # ================= CRUD =================
    path('electricians/', views.electricians),
    path('delete-electrician/<int:id>/', views.delete_electrician),

    path('jobs/', views.jobs),
    path('delete-job/<int:id>/', views.delete_job),

    path('tasks/', views.tasks),
    path('delete-task/<int:id>/', views.delete_task),

    path('materials/', views.materials),
    path('delete-material/<int:id>/', views.delete_material),

    # ================= OTHER =================
    path('reports/', views.reports),
    path('profile/', views.profile),
    path('my-requests/', views.my_requests),

    # ================= API (IMPORTANT 🔥) =================
    path('api/tasks/', views.api_tasks),
    path('api/tasks/add/', views.api_add_task),
    path('api/tasks/update/<int:id>/', views.api_update_task),
    path('api/tasks/delete/<int:id>/', views.api_delete_task),
]