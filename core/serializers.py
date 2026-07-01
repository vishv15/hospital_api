from rest_framework import serializers
from core.models import Headquarters, SubHeadquarters, Doctor, Visit, VisitStatus
from accounts.models import User, Role
from accounts.serializers import UserSerializer

class HeadquartersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headquarters
        fields = '__all__'


class SubHeadquartersSerializer(serializers.ModelSerializer):
    headquarters_name = serializers.CharField(source='headquarters.name', read_only=True)

    class Meta:
        model = SubHeadquarters
        fields = '__all__'

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            return attrs
        
        user = request.user
        hq = attrs.get('headquarters')

        # HQ Admin can only create/update SubHQs for their assigned HQ
        if user.role == Role.HQ_ADMIN:
            if hq and hq != user.headquarters:
                raise serializers.ValidationError({"headquarters": "You can only manage sub headquarters for your own headquarters."})
            # Force assigned HQ
            attrs['headquarters'] = user.headquarters

        return attrs


class DoctorSerializer(serializers.ModelSerializer):
    headquarters_name = serializers.CharField(source='headquarters.name', read_only=True)
    sub_headquarters_name = serializers.CharField(source='sub_headquarters.name', read_only=True)
    assigned_mrs_details = UserSerializer(source='assigned_mrs', many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialization', 'phone', 'email',
            'headquarters', 'headquarters_name', 'sub_headquarters', 'sub_headquarters_name',
            'assigned_mrs', 'assigned_mrs_details', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            return attrs
        
        user = request.user
        hq = attrs.get('headquarters')
        sub_hq = attrs.get('sub_headquarters')
        assigned_mrs = attrs.get('assigned_mrs', [])

        # Validate that sub_hq belongs to hq if both are provided
        if sub_hq and hq and sub_hq.headquarters != hq:
            raise serializers.ValidationError({"sub_headquarters": "The sub headquarters must belong to the selected headquarters."})

        # Enforce scope based on role
        if user.role == Role.HQ_ADMIN:
            # Force doctor's HQ to match Admin's HQ
            attrs['headquarters'] = user.headquarters
            if sub_hq and sub_hq.headquarters != user.headquarters:
                raise serializers.ValidationError({"sub_headquarters": "The sub headquarters must belong to your headquarters."})
            
        elif user.role == Role.HQ_STAFF:
            # Force doctor's HQ to match Staff's HQ
            attrs['headquarters'] = user.headquarters
            if sub_hq and sub_hq.headquarters != user.headquarters:
                raise serializers.ValidationError({"sub_headquarters": "The sub headquarters must belong to your headquarters."})
            
        elif user.role == Role.SUB_HQ_STAFF:
            # Force doctor's HQ and SubHQ to match Staff's assigned SubHQ
            if not user.sub_headquarters:
                raise serializers.ValidationError({"detail": "Sub HQ Staff must be assigned to a sub headquarters first."})
            attrs['headquarters'] = user.sub_headquarters.headquarters
            attrs['sub_headquarters'] = user.sub_headquarters

        # Validate that all assigned MRs are actually MRs and belong to the correct HQ
        for mr in assigned_mrs:
            if mr.role != Role.MR:
                raise serializers.ValidationError({"assigned_mrs": f"User {mr.username} is not a Medical Representative (MR)."})
            
            # Non-super admin can only assign MRs from their own HQ
            if user.role != Role.SUPER_ADMIN:
                if mr.headquarters != user.headquarters:
                    raise serializers.ValidationError({"assigned_mrs": f"MR {mr.username} does not belong to your headquarters."})

        return attrs


class VisitSerializer(serializers.ModelSerializer):
    mr_details = UserSerializer(source='mr', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)

    class Meta:
        model = Visit
        fields = [
            'id', 'mr', 'mr_details', 'doctor', 'doctor_name', 'doctor_specialization',
            'date', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user:
            return attrs
        
        user = request.user
        mr = attrs.get('mr')
        doctor = attrs.get('doctor')

        # If user is MR, they can only create/update visits for themselves
        if user.role == Role.MR:
            attrs['mr'] = user
            mr = user
            
            # Check if doctor is assigned to this MR
            # An MR can only mark visits for doctors assigned to them
            if doctor and not doctor.assigned_mrs.filter(id=user.id).exists():
                raise serializers.ValidationError({"doctor": "You can only mark visits for doctors assigned to you."})
        
        else:
            # If creator is not MR, we must ensure the assigned mr is actually an MR
            if mr and mr.role != Role.MR:
                raise serializers.ValidationError({"mr": "Assigned user is not a Medical Representative."})

            # Check hierarchy rules for non-super admins creating visits
            if user.role == Role.HQ_ADMIN:
                if mr and mr.headquarters != user.headquarters:
                    raise serializers.ValidationError({"mr": "The MR must belong to your headquarters."})
                if doctor and doctor.headquarters != user.headquarters:
                    raise serializers.ValidationError({"doctor": "The doctor must belong to your headquarters."})

            elif user.role == Role.HQ_STAFF:
                if mr and mr.headquarters != user.headquarters:
                    raise serializers.ValidationError({"mr": "The MR must belong to your headquarters."})
                if doctor and doctor.headquarters != user.headquarters:
                    raise serializers.ValidationError({"doctor": "The doctor must belong to your headquarters."})

            elif user.role == Role.SUB_HQ_STAFF:
                if not user.sub_headquarters:
                    raise serializers.ValidationError({"detail": "Sub HQ Staff must be assigned to a sub headquarters first."})
                if mr and mr.sub_headquarters != user.sub_headquarters:
                    raise serializers.ValidationError({"mr": "The MR must belong to your assigned sub headquarters."})
                if doctor and doctor.sub_headquarters != user.sub_headquarters:
                    raise serializers.ValidationError({"doctor": "The doctor must belong to your assigned sub headquarters."})

        return attrs
