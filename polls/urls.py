from django.urls import path
from . import views
from .views import StudentLoginView

app_name = 'polls'

urlpatterns = [
    path('', views.PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:pk>/', views.PollDetailView.as_view(), name='poll-detail'),
    path('vote/', views.cast_vote, name='cast-vote'),
    path('<int:poll_id>/results/', views.poll_results, name='poll-results'),
    path('my-votes/', views.user_votes, name='user-votes'),
    path('my-polls/', views.my_polls, name='my-polls'),
    path('student/login/', StudentLoginView.as_view(), name='student-login'),
]