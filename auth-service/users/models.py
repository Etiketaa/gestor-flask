from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizations'

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=50)  # admin, venta, depo, contador
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        unique_together = ('name', 'organization')

    def __str__(self):
        return f"{self.name} ({self.organization.slug})"


class User(AbstractUser):
    # Se reutiliza username, password de AbstractUser
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='users', null=True, blank=True
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    status = models.CharField(
        max_length=20, default='pending'  # pending, approved, rejected
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        unique_together = ('username', 'organization')

    def __str__(self):
        return self.username
