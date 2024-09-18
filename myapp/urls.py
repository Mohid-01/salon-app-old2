from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SalonViewSet, AppointmentViewSet, FavoriteViewSet, check_email_exists, login_view, add_to_favorites, schedule_appointment, cancel_appointment #LoginView
from . import views

# Set up the router for your viewsets
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('salons', SalonViewSet)
router.register('appointments', AppointmentViewSet)
router.register('favorites', FavoriteViewSet)

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the routes from the router    
    path('check-email/', check_email_exists, name='check_email_exists'),  # Custom endpoint for email check
    #path('login/', LoginView.as_view(), name='login'),
    path('login/', login_view, name='login'),
    path('users/<int:user_id>/', views.get_user, name='get_user'),
    path('salons/<int:salon_id>/', views.get_salon, name='get_salon'),
    path('favorites/', views.get_favorites, name='get_favorites'),
    path('add-to-favorites/', add_to_favorites, name='add_to_favorites'),
    path('schedule-appointment/', schedule_appointment, name='schedule_appointment'),
    path('cancel-booking/<int:appointment_id>/', cancel_appointment, name='cancel_booking'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


'''
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('salons/', views.salon_list, name='salon_list'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('favorites/', views.favorite_list, name='favorite_list'),
]
'''
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SalonViewSet, AppointmentViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'salons', SalonViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
"""