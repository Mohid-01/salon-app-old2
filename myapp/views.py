from django.http import JsonResponse, HttpResponseNotAllowed, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, Salon, Appointment, Favorite
from .serializers import UserSerializer, SalonSerializer, AppointmentSerializer, FavoriteSerializer
import json
from django.utils.dateparse import parse_datetime
from datetime import datetime

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Use the custom User model
    serializer_class = UserSerializer

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    def get_queryset(self):
        user_id = self.request.query_params.get('user')
        if user_id:
            return Appointment.objects.filter(user_id=user_id)
        return Appointment.objects.all()

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            return JsonResponse({
                'message': 'Login successful',
                'user_id': user.pk  # Use 'pk' to get the primary key of the user
            }, status=200)
        else:
            # Invalid credentials
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)

@api_view(['GET'])
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['GET'])
def get_salon(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id)
        serializer = SalonSerializer(salon)
        return Response(serializer.data)
    except Salon.DoesNotExist:
        return Response({'error': 'Salon not found'}, status=404)

@api_view(['GET'])
def get_favorites(request):
    favorites = Favorite.objects.all()
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def check_email_exists(request):
    email = request.data.get('email')
    if User.objects.filter(email=email).exists():
        return Response({"exists": True})
    else:
        return Response({"exists": False})

@api_view(['POST'])
def add_to_favorites(request):
    user = request.user
    salon_id = request.data.get('salon_id')
    

    if not salon_id:
        return Response({'error': 'Salon ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        salon = Salon.objects.get(id=salon_id)
    except Salon.DoesNotExist:
        return Response({'error': 'Salon not found'}, status=status.HTTP_404_NOT_FOUND)

    favorite, created = Favorite.objects.get_or_create(user=user, salon=salon)
    if created:
        return Response({'message': 'Added to favorites'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already in favorites'}, status=status.HTTP_200_OK)


User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # This will allow requests without login
def schedule_appointment(request):
    user_id = request.data.get('user_id')
    salon_id = request.data.get('salon_id')
    appointment_date_str = request.data.get('appointment_date')

    if not user_id or not salon_id or not appointment_date_str:
        return Response({'error': 'User ID, Salon ID, and appointment date are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)  # Make sure user_id is correctly passed from the frontend
        salon = Salon.objects.get(salon_id=salon_id)
        appointment_date = parse_datetime(appointment_date_str)
        if not appointment_date:
            raise ValueError('Invalid date format')
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Salon.DoesNotExist:
        return Response({'error': 'Salon not found'}, status=status.HTTP_404_NOT_FOUND)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.create(user=user, salon=salon, appointment_date=appointment_date)
    serializer = AppointmentSerializer(appointment)
    return Response({'message': 'Appointment scheduled', 'appointment': serializer.data}, status=status.HTTP_201_CREATED)
"""
@csrf_exempt  # This disables CSRF protection for this view
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow requests without login, authenticate manually
def schedule_appointment(request):
    user = request.user
    salon_id = request.data.get('salon_id')  # Make sure this is correctly passed from the frontend
    appointment_date_str = request.data.get('appointment_date')

    if not salon_id or not appointment_date_str:
        return Response({'error': 'Salon ID and appointment date are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Updated query to use salon_id
        salon = Salon.objects.get(salon_id=salon_id)  # Use 'salon_id' if it's a custom field, otherwise 'id'
        appointment_date = parse_datetime(appointment_date_str)
        if not appointment_date:
            raise ValueError('Invalid date format')
    except Salon.DoesNotExist:
        return Response({'error': 'Salon not found'}, status=status.HTTP_404_NOT_FOUND)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.create(user=user, salon=salon, appointment_date=appointment_date)
    serializer = AppointmentSerializer(appointment)
    return Response({'message': 'Appointment scheduled', 'appointment': serializer.data}, status=status.HTTP_201_CREATED)
"""

@api_view(['GET'])
def get_appointments(request, user_id):
    # Fetch appointments with related salon data
    appointments = Appointment.objects.filter(user_id=user_id).select_related('salon')
    
    appointments_data = []
    for appointment in appointments:
        appointments_data.append({
            'user': appointments.user_id,
            'appointment_id': appointment.appointment_id,
            'appointment_date': appointment.appointment_date,
            'salon_name': appointment.salon.name,  # Include the salon name
            #'booking_details': f"Appointment at {appointment.salon.name} on {appointment.appointment_date}",
        })
    
    return JsonResponse(appointments_data, safe=False)


'''
@api_view(['GET'])
def get_salon_details(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id)
        
        # Prepare the response data with the requested fields
        salon_data = {
            'salon_id': salon.id,               # Salon ID
            'name': salon.name,                 # Salon name
            'address': salon.address,           # Address
            'location': salon.location,         # Location (if it's a field, otherwise you can modify it)
            'city': salon.city,                 # City
            'desc': salon.description,          # Description (assuming you have a 'description' field)
            'image': salon.image_url,           # Image URL (or 'image' if you store the image differently)
        }
        
        return JsonResponse(salon_data)
    except Salon.DoesNotExist:
        raise Http404("Salon not found")
    '''

def convert_date_to_datetime(date_only):
    # Convert a date object to a datetime object at the start of the day
    return datetime.combine(date_only, datetime.min.time())

@csrf_exempt
@require_http_methods(["DELETE"])
def cancel_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(appointment_id=appointment_id)
        appointment.delete()
        return JsonResponse({'message': 'Booking canceled successfully.'}, status=200)
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Booking not found.'}, status=404)




"""
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            # Invalid credentials
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=400)

"""
   
'''
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                # If login is successful, you might want to return a token or user info
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''
'''
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        #data = json.loads(request.body)
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Login successful, return response
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            # Invalid credentials
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        '''
     

'''
from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Salon, Appointment, Favorite
# Create your views here.

def user_list(request):
    users = list(User.objects.values())
    return JsonResponse(users, safe=False)

def salon_list(request):
    salons = list(Salon.objects.values())
    return JsonResponse(salons, safe=False)

def appointment_list(request):
    appointments = list(Appointment.objects.values())
    return JsonResponse(appointments, safe=False)

def favorite_list(request):
    favorites = list(Favorite.objects.values())
    return JsonResponse(favorites, safe=False) 
'''
"""
from rest_framework import viewsets
from .models import User, Salon, Appointment, Favorite
from .serializers import UserSerializer, SalonSerializer, AppointmentSerializer, FavoriteSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
"""