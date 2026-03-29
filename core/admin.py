from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Electrician)
admin.site.register(Job)
admin.site.register(Task)
admin.site.register(Material)