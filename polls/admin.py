from django.contrib import admin
from django.db.models import Count
from .models import Poll, PollOption, Vote, Student

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'expires_at', 'is_active', 'total_votes']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_votes']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            vote_count=Count('options__votes')
        )
    
    def total_votes(self, obj):
        return obj.vote_count
    total_votes.admin_order_field = 'vote_count'

@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'poll', 'vote_count']
    list_filter = ['poll']
    search_fields = ['text', 'poll__title']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            vote_count=Count('votes')
        )
    
    def vote_count(self, obj):
        return obj.vote_count
    vote_count.admin_order_field = 'vote_count'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'option', 'voted_at', 'ip_address']
    list_filter = ['voted_at', 'option__poll']
    search_fields = ['user__username', 'option__text']
    readonly_fields = ['voted_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['index_number', 'full_name', 'created_at']
    search_fields = ['index_number', 'full_name']
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        # If this is a new student or PIN was changed
        if not change or 'pin' in form.changed_data:
            # Get the raw PIN from the form
            raw_pin = form.cleaned_data.get('pin')
            if raw_pin:
                obj.set_pin(raw_pin)  # Hash the PIN
        super().save_model(request, obj, form, change)