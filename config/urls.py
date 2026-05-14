from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core import views


urlpatterns = [

    # ================= ADMIN =================

    path('admin/', admin.site.urls),


    # ================= AUTH =================

    path('', views.home),

    path('login/', views.login_view),

    path('register/', views.register),

    path('logout/', views.logout),



    # ================= DASHBOARD =================

    path('dashboard/', views.dashboard),

    path(
        'client-dashboard/',
        views.client_dashboard,
        name='client_dashboard'
    ),


    # ================= ELECTRICIANS =================

    path('electricians/', views.electricians),

    path(
        'delete-electrician/<int:id>/',
        views.delete_electrician
    ),


    # ================= JOBS =================

    path('jobs/', views.jobs),

    path(
        'delete-job/<int:id>/',
        views.delete_job
    ),


    # ================= TASKS =================

    path('tasks/', views.tasks),

    path(
        'delete-task/<int:id>/',
        views.delete_task
    ),


    # ================= MATERIALS =================

    path('materials/', views.materials),

    path(
        'delete-material/<int:id>/',
        views.delete_material
    ),


    # ================= REPORTS =================

    path('reports/', views.reports),

    path(
        'upload-report/',
        views.upload_report,
        name='upload_report'
    ),


    # ================= PROFILE =================

    path('profile/', views.profile),

    path('my-requests/', views.my_requests),


    # ================= CLIENT REQUESTS =================

    path(
        'client-requests/',
        views.client_requests
    ),


    # ================= PAYMENTS =================

    path(
        'payments/',
        views.payments,
        name='payments'
    ),


    # ================= API =================

    path('api/tasks/', views.api_tasks),

    path(
        'api/tasks/add/',
        views.api_add_task
    ),

    path(
        'api/tasks/update/<int:id>/',
        views.api_update_task
    ),

    path(
        'api/tasks/delete/<int:id>/',
        views.api_delete_task
    ),

    path(
    'payment-success/',
    views.payment_success,
    name='payment_success'
    ),

]


# ================= MEDIA =================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )