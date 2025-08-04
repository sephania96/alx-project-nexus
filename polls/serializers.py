from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Poll, PollOption, Vote

class PollOptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.ReadOnlyField()
    vote_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = PollOption
        fields = ['id', 'text', 'vote_count', 'vote_percentage']

class PollOptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['text']

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    total_votes = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by', 'created_at', 
            'updated_at', 'expires_at', 'is_active', 'allow_multiple_votes',
            'options', 'total_votes', 'is_expired'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class PollCreateSerializer(serializers.ModelSerializer):
    options = PollOptionCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'expires_at', 'is_active', 
            'allow_multiple_votes', 'options'
        ]
    
    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value
    
    def validate_options(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Poll must have at least 2 options")
        if len(value) > 10:
            raise serializers.ValidationError("Poll cannot have more than 10 options")
        
        option_texts = [option['text'] for option in value]
        if len(option_texts) != len(set(option_texts)):
            raise serializers.ValidationError("Poll options must be unique")
        
        return value
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        
        for option_data in options_data:
            PollOption.objects.create(poll=poll, **option_data)
        
        return poll

class VoteSerializer(serializers.ModelSerializer):
    option_text = serializers.CharField(source='option.text', read_only=True)
    poll_title = serializers.CharField(source='option.poll.title', read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'option', 'option_text', 'poll_title', 'voted_at']
        read_only_fields = ['voted_at']
    
    def validate_option(self, value):
        poll = value.poll
        user = self.context['request'].user
        
        # Check if poll is active
        if not poll.is_active:
            raise serializers.ValidationError("Poll is not active")
        
        # Check if poll is expired
        if poll.is_expired:
            raise serializers.ValidationError("Poll has expired")
        
        # Check if user already voted (if multiple votes not allowed)
        if not poll.allow_multiple_votes:
            existing_vote = Vote.objects.filter(
                user=user,
                option__poll=poll
            ).exists()
            
            if existing_vote:
                raise serializers.ValidationError("You have already voted in this poll")
        
        return value

class PollResultSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_at', 'expires_at',
            'is_expired', 'total_votes', 'options'
        ]

class StudentLoginSerializer(serializers.Serializer):
    index_number = serializers.CharField()
    pin = serializers.CharField()

    def validate(self, data):
        try:
            student = Student.objects.get(index_number=data['index_number'])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Invalid index number or PIN.")

        if not student.check_pin(data['pin']):
            raise serializers.ValidationError("Invalid index number or PIN.")

        data['student'] = student
        return data

class StudentVoteSerializer(serializers.ModelSerializer):
    index_number = serializers.CharField(write_only=True)
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = Vote
        fields = ['option', 'index_number', 'pin']

    def validate(self, data):
        try:
            student = Student.objects.get(index_number=data['index_number'])
        except Student.DoesNotExist:
            raise serializers.ValidationError("Invalid index number or PIN.")

        if not student.check_pin(data['pin']):
            raise serializers.ValidationError("Invalid index number or PIN.")

        poll = data['option'].poll
        
        # Check if poll is active and not expired
        if not poll.is_active:
            raise serializers.ValidationError("Poll is not active")
        
        if poll.is_expired:
            raise serializers.ValidationError("Poll has expired")

        # Check if student already voted
        if Vote.objects.filter(user__isnull=True, option__poll=poll).filter(
            # We'll use a custom field to link to student
        ).exists():
            # For now, we'll create a new vote model later
            pass

        data['student'] = student
        return data