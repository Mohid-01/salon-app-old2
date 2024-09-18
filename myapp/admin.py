from django.contrib import admin
from .models import User, Salon, Appointment, Favorite

# Register your models here.
admin.site.register(User)
admin.site.register(Salon)
admin.site.register(Appointment)
admin.site.register(Favorite)
