from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Organization, Role, User


class OrganizationRegisterSerializer(serializers.Serializer):
    organization_name = serializers.CharField(required=True)
    organization_slug = serializers.SlugField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)

    def validate_organization_slug(self, value):
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError('La organización ya existe.')
        return value

    def validate_username(self, value):
        # validación simple; la unicidad real se chequea por organization
        return value

    def create(self, validated_data):
        org = Organization.objects.create(
            name=validated_data['organization_name'],
            slug=validated_data['organization_slug'],
        )
        admin_role = Role.objects.create(name='admin', organization=org)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            organization=org,
            role=admin_role,
            status='approved',
        )
        return {'organization': org, 'user': user}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    organization_slug = serializers.SlugField(required=True)

    def validate(self, attrs):
        org = Organization.objects.filter(slug=attrs['organization_slug']).first()
        if not org:
            raise serializers.ValidationError('Organización no encontrada.')

        user = authenticate(
            username=attrs['username'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('Credenciales inválidas.')
        if user.organization_id != org.id:
            raise serializers.ValidationError('El usuario no pertenece a esta organización.')
        if user.status != 'approved':
            raise serializers.ValidationError(f'Cuenta {user.status}.')

        attrs['user'] = user
        attrs['organization'] = org
        return attrs


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='role.name', read_only=True)
    organization = serializers.CharField(source='organization.slug', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'organization', 'status')
