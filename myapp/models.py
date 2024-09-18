from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager #User
from django.contrib.auth.hashers import make_password

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # Password will be hashed automatically
    date_of_birth = models.DateField()
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # Ensure 'name' is included when creating superusers

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

'''
class User(models.Model):
    user = User.objects.create_user(name='name', email='email', password='password')
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField()
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name
'''
class Salon(models.Model):
    salon_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    location = models.URLField(max_length=300)  # Assuming you’re storing a Google Maps URL
    city = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    image = models.ImageField(null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Foreign key to User model
    salon = models.ForeignKey('Salon', on_delete=models.CASCADE)  # Foreign key to Salon model
    appointment_date = models.DateTimeField()

    def __str__(self):
        return f"Appointment for {self.user.name} at {self.salon.name} on {self.appointment_date}"

class Favorite(models.Model):
    favorite_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Foreign key to User model
    salon = models.ForeignKey('Salon', on_delete=models.CASCADE)  # Foreign key to Salon model

    def __str__(self):
        return f"{self.user.name} favorited {self.salon.name}"
    
