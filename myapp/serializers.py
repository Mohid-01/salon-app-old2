from rest_framework import serializers
from django.contrib.auth.models import User #New
from .models import User, Salon, Appointment, Favorite

class UserSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    #date_of_birth = serializers.DateField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'date_of_birth', 'city']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = '__all__'

"""
class AppointmentSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['appointment_id', 'user', 'salon_name', 'appointment_date']


"""
class AppointmentSerializer(serializers.ModelSerializer):
    #salon_name = serializers.CharField(source='salon.name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['appointment_id', 'user', 'salon' , 'appointment_date'] #, 'booking_details'



#class AppointmentSerializer(serializers.ModelSerializer):
#    appointment_date = serializers.DateTimeField()  # Use DateTimeField for datetime objects
#    class Meta:
#        model = Appointment
#        fields = '__all__'

#class FavoriteSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Favorite
#        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'salon']
        extra_kwargs = {
            'user': {'required': True},
            'salon': {'required': True},
        }

    def create(self, validated_data):
        # Debugging statement to check the validated data
        print("Validated data:", validated_data)
        return super().create(validated_data)
    #user = UserSerializer(read_only=True)
    #salon = SalonSerializer(read_only=True)

    #class Meta:
    #    model = Favorite
    #    fields = ['user', 'salon']





    #def create(self, validated_data):
        # Create a new user with a hashed password
       # user = User.objects.create(
        #    username=validated_data['username'],
         #   email=validated_data['email'],
          #  password=validated_data['password'],
           # date_of_birth=validated_data.get('date_of_birth'),
            #city=validated_data['city']
        #)
        #user.set_password(validated_data.get('password'))
        #user.save()
        #return user
    
#class UserSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = User
   #     #fields = '__all__'
    #    fields = ['name', 'email', 'password', 'dob', 'city']