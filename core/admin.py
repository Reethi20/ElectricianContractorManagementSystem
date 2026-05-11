from django.contrib import admin
from .models import (
    User,
    Electrician,
    Job,
    Task,
    Material
)
admin.site.register(User)
admin.site.register(Electrician)
admin.site.register(Job)
admin.site.register(Task)
admin.site.register(Material)