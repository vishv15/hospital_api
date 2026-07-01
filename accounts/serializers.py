from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import User, Role
from core.models import Headquarters, SubHeadquarters

class UserSerializer(serializers.ModelSerializer):
    headquarters_name = serializers.CharField(source='headquarters.name', read_only=True)
    sub_headquarters_name = serializers.CharField(source='sub_headquarters.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'headquarters', 'headquarters_name',
            'sub_headquarters', 'sub_headquarters_name', 'is_active', 'date_joined'
        ]
        read_only_fields = ['is_active', 'date_joined']


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name',
            'role', 'headquarters', 'sub_headquarters', 'is_active'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            return attrs
        
        creator = request.user
        role = attrs.get('role')
        hq = attrs.get('headquarters')
        sub_hq = attrs.get('sub_headquarters')

       
        if creator.role == Role.SUPER_ADMIN:
            
            if sub_hq and hq and sub_hq.headquarters != hq:
                raise serializers.ValidationError({"sub_headquarters": "The sub headquarters must belong to the selected headquarters."})
            return attrs


        if creator.role == Role.HQ_ADMIN:
            
            if role in [Role.SUPER_ADMIN, Role.HQ_ADMIN]:
                raise serializers.ValidationError({"role": "HQ Admin cannot create Super Admin or HQ Admin users."})
            
      
            if hq and hq != creator.headquarters:
                raise serializers.ValidationError({"headquarters": "You can only assign users to your own headquarters."})
            
           
            if sub_hq and sub_hq.headquarters != creator.headquarters:
                raise serializers.ValidationError({"sub_headquarters": "The sub headquarters must belong to your headquarters."})
            
    
            attrs['headquarters'] = creator.headquarters

        return attrs

    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        else:
        
            validated_data['password'] = make_password(validated_data.get('username'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
