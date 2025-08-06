from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Poll, PollOption, Vote
from .models import Student
from .serializers import StudentLoginSerializer
from .serializers import (
    PollSerializer, PollCreateSerializer, VoteSerializer, 
    PollResultSerializer
)
from rest_framework.views import APIView

class PollListCreateView(generics.ListCreateAPIView):
    """
    List all polls or create a new poll.
    """
    queryset = Poll.objects.prefetch_related('options').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get list of all polls",
        responses={200: PollSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new poll",
        request_body=PollCreateSerializer,
        responses={
            201: PollSerializer,
            400: "Bad Request"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a poll.
    """
    queryset = Poll.objects.prefetch_related('options').all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Get poll details",
        responses={
            200: PollSerializer,
            404: "Poll not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@swagger_auto_schema(
    method='post',
    operation_description="Cast a vote for a poll option",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['option_id'],
        properties={
            'option_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the poll option to vote for'
            )
        }
    ),
    responses={
        201: VoteSerializer,
        400: "Bad Request",
        401: "Authentication required"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cast_vote(request):
    """
    Cast a vote for a specific poll option.
    """
    option_id = request.data.get('option_id')
    
    if not option_id:
        return Response(
            {'error': 'option_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        option = PollOption.objects.get(id=option_id)
    except PollOption.DoesNotExist:
        return Response(
            {'error': 'Poll option not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get client IP
    ip_address = request.META.get('REMOTE_ADDR')
    
    vote_data = {
        'option': option.id,
        'user': request.user.id,
        'ip_address': ip_address
    }
    
    serializer = VoteSerializer(data=vote_data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save(user=request.user, ip_address=ip_address)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_description="Get real-time poll results",
    responses={
        200: PollResultSerializer,
        404: "Poll not found"
    }
)
@api_view(['GET'])
def poll_results(request, poll_id):
    """
    Get real-time results for a specific poll.
    """
    poll = get_object_or_404(
        Poll.objects.prefetch_related(
            Prefetch('options', queryset=PollOption.objects.annotate(
                vote_count=Count('votes')
            ))
        ),
        id=poll_id
    )
    
    serializer = PollResultSerializer(poll)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_description="Get user's voting history",
    responses={200: VoteSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_votes(request):
    """
    Get current user's voting history.
    """
    votes = Vote.objects.filter(user=request.user).select_related(
        'option', 'option__poll'
    ).order_by('-voted_at')
    
    serializer = VoteSerializer(votes, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_description="Get polls created by current user",
    responses={200: PollSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_polls(request):
    """
    Get polls created by the current user.
    """
    polls = Poll.objects.filter(created_by=request.user).prefetch_related('options')
    serializer = PollSerializer(polls, many=True)
    return Response(serializer.data)

class StudentLoginView(generics.CreateAPIView):
    """
    Student login with index number and PIN
    """
    serializer_class = StudentLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Student login with index number and PIN",
        request_body=StudentLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'student_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'index_number': openapi.Schema(type=openapi.TYPE_STRING),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            return Response({
                'student_id': student.id,
                'index_number': student.index_number,
                'full_name': student.full_name,
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_description="Student vote with index number and PIN",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['index_number', 'pin', 'option_id'],
        properties={
            'index_number': openapi.Schema(type=openapi.TYPE_STRING),
            'pin': openapi.Schema(type=openapi.TYPE_STRING),
            'option_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ),
    responses={
        201: "Vote recorded successfully",
        400: "Bad Request",
        404: "Option not found"
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def student_vote(request):
    """
    Student vote with authentication
    """
    index_number = request.data.get('index_number')
    pin = request.data.get('pin')
    option_id = request.data.get('option_id')
    
    if not all([index_number, pin, option_id]):
        return Response(
            {'error': 'index_number, pin, and option_id are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate student
    try:
        student = Student.objects.get(index_number=index_number)
        if not student.check_pin(pin):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Student.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get poll option
    try:
        option = PollOption.objects.get(id=option_id)
    except PollOption.DoesNotExist:
        return Response(
            {'error': 'Poll option not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if student already voted 
    # Check if student already voted on this poll
    existing_vote = Vote.objects.filter(
        student=student,
        option__poll=option.poll
    ).exists()

    if existing_vote:
        return Response(
            {'error': 'You have already voted in this poll'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create the vote
    vote = Vote.objects.create(
        student=student,
        option=option,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    return Response({
        'message': 'Vote recorded successfully',
        'student': student.index_number,
        'poll': option.poll.title,
        'choice': option.text,
        'vote_id': vote.id
    }, status=status.HTTP_201_CREATED)