from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from .models import User, Role, Question, AuditLog
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    QuestionForm,
)


def home(request):
    """Home page view."""
    questions_count = Question.objects.filter(is_active=True).count()
    return render(request, 'quiz/home.html', {'questions_count': questions_count})


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Log the login action
                AuditLog.objects.create(
                    user=user,
                    action='login',
                    model_name='User',
                    object_id=user.id,
                    details=f'User {user.username} logged in',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'quiz/login.html', {'form': form})


def user_logout(request):
    """User logout view."""
    if request.user.is_authenticated:
        # Log the logout action
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            model_name='User',
            object_id=request.user.id,
            details=f'User {request.user.username} logged out',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Assign standard role by default
            standard_role, _ = Role.objects.get_or_create(
                name=Role.STANDARD,
                defaults={'description': 'Standard user with basic access'}
            )
            user.role = standard_role
            user.save()
            
            # Log the registration action
            AuditLog.objects.create(
                user=user,
                action='create',
                model_name='User',
                object_id=user.id,
                details=f'New user {user.username} registered',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to QuizQuest!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'quiz/register.html', {'form': form})


def admin_required(view_func):
    """Decorator to require admin role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            return HttpResponseForbidden('Admin access required.')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard placeholder view."""
    users_count = User.objects.count()
    questions_count = Question.objects.count()
    recent_logs = AuditLog.objects.all()[:10]
    
    context = {
        'users_count': users_count,
        'questions_count': questions_count,
        'recent_logs': recent_logs,
    }
    return render(request, 'quiz/admin_dashboard.html', context)


# Question CRUD Views
@login_required
def question_list(request):
    """List all questions."""
    questions = Question.objects.filter(is_active=True)
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quiz/question_list.html', {'page_obj': page_obj})


@login_required
@admin_required
def question_create(request):
    """Create a new question."""
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='Question',
                object_id=question.id,
                details=f'Question "{question.title}" created',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Question created successfully!')
            return redirect('question_list')
    else:
        form = QuestionForm()
    
    return render(request, 'quiz/question_form.html', {'form': form, 'action': 'Create'})


@login_required
def question_detail(request, pk):
    """View question details."""
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'quiz/question_detail.html', {'question': question})


@login_required
@admin_required
def question_update(request, pk):
    """Update a question."""
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='Question',
                object_id=question.id,
                details=f'Question "{question.title}" updated',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Question updated successfully!')
            return redirect('question_detail', pk=question.pk)
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'quiz/question_form.html', {
        'form': form,
        'action': 'Update',
        'question': question
    })


@login_required
@admin_required
def question_delete(request, pk):
    """Delete a question (soft delete)."""
    question = get_object_or_404(Question, pk=pk)
    
    if request.method == 'POST':
        question.is_active = False
        question.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Question',
            object_id=question.id,
            details=f'Question "{question.title}" deleted',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Question deleted successfully!')
        return redirect('question_list')
    
    return render(request, 'quiz/question_confirm_delete.html', {'question': question})


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
