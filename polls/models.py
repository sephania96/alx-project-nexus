from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Poll(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_polls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    allow_multiple_votes = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def total_votes(self):
        return Vote.objects.filter(option__poll=self).count()
    
    def clean(self):
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiry date must be in the future")

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['poll', 'text']
        indexes = [
            models.Index(fields=['poll']),
        ]
    
    def __str__(self):
        return f"{self.poll.title} - {self.text}"
    
    def vote_count(self):  # Method instead of @property
        return self.votes.count()

    vote_count.short_description = 'Vote Count'  # For admin display
    @property
    def vote_percentage(self):
        total_votes = self.poll.total_votes
        if total_votes == 0:
            return 0
        return round((self.vote_count() / total_votes) * 100, 2)  # Note: vote_count() with parentheses

class Student(models.Model):
    index_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    pin = models.CharField(max_length=128)  # Store hashed PIN
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['index_number']),
        ]
    
    def set_pin(self, raw_pin):
        self.pin = make_password(raw_pin)
    
    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.pin)
    
    def __str__(self):
        return f"{self.index_number} - {self.full_name}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        # Update constraints
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'option'],
                condition=models.Q(user__isnull=False),
                name='unique_user_vote'
            ),
            models.UniqueConstraint(
                fields=['student', 'option'],
                condition=models.Q(student__isnull=False),
                name='unique_student_vote'
            ),
        ]
    
    indexes = [
            models.Index(fields=['user', 'option']),
            models.Index(fields=['student', 'option']),  # Add this
            models.Index(fields=['voted_at']),
            models.Index(fields=['option']),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} voted for {self.option.text}"
        elif self.student:
            return f"{self.student.index_number} voted for {self.option.text}"
        return f"Anonymous vote for {self.option.text}"

    def clean(self):
        # Ensure either user or student is set, but not both
        if not self.user and not self.student:
            raise ValidationError("Either user or student must be set")
        if self.user and self.student:
            raise ValidationError("Cannot set both user and student")
        
        # Check if poll allows multiple votes
        if not self.option.poll.allow_multiple_votes:
            existing_vote = None
            if self.user:
                existing_vote = Vote.objects.filter(
                    user=self.user,
                    option__poll=self.option.poll
                ).exclude(pk=self.pk).exists()
            elif self.student:
                existing_vote = Vote.objects.filter(
                    student=self.student,
                    option__poll=self.option.poll
                ).exclude(pk=self.pk).exists()
            
            if existing_vote:
                raise ValidationError("Already voted in this poll")
        
        # Check if poll is expired
        if self.option.poll.is_expired:
            raise ValidationError("Cannot vote on expired poll")
        
        # Check if poll is active
        if not self.option.poll.is_active:
            raise ValidationError("Cannot vote on inactive poll")
        