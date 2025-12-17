from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import random


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='STUDENT', first_name='', last_name=''):
        if not email:
            raise ValueError("Email requis")
        if not email.endswith("@supnum.mr"):
            raise ValueError("Email SupNum requis")

        user = self.model(
            email=self.normalize_email(email),
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
            role='ADMIN',
            first_name='Admin',
            last_name='SupNum'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('ADMIN', 'Admin'),
        ('AGENT', 'Agent'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True, max_length=190)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class PasswordResetCode(models.Model):
    """Modèle pour stocker les codes de réinitialisation de mot de passe"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            # Générer un code de 6 chiffres
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            # Le code expire après 15 minutes
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Vérifie si le code est encore valide"""
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Code {self.code} pour {self.user.email}"
