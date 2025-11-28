from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .models import Profile, Quiz, Question, Choice, QuizSubmission, Answer


def home(request):
    context = {"year": datetime.now().year}
    return render(request, "home.html", context)


# ---------- AUTH VIEWS ----------

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "STUDENT")  # 'ADMIN' or 'STUDENT'

        # basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        Profile.objects.create(user=user, role=role)

        messages.success(request, "Account created. You can now log in.")
        return redirect("login")

    return render(request, "auth_register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "auth_login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard(request):
    """
    Dashboard for both roles:
    - STUDENT: show their activity, recent submissions, basic stats
    - ADMIN: show system-wide stats and latest quizzes/submissions
    """
    user = request.user
    profile = getattr(user, "profile", None)
    role = getattr(profile, "role", "STUDENT")

    context = {
        "user": user,
        "role": role,
    }

    if role == "ADMIN":
        # --- ADMIN VIEW DATA ---
        total_users = Profile.objects.count()
        total_quizzes = Quiz.objects.count()
        total_questions = Question.objects.count()
        total_submissions = QuizSubmission.objects.count()

        latest_quizzes = Quiz.objects.order_by("-created_at")[:5]  # Quiz HAS created_at
        latest_submissions = (
            QuizSubmission.objects.select_related("user", "quiz")
            .order_by("-submitted_at")[:5]   # use submitted_at here
        )

        context.update({
            "is_admin": True,
            "total_users": total_users,
            "total_quizzes": total_quizzes,
            "total_questions": total_questions,
            "total_submissions": total_submissions,
            "latest_quizzes": latest_quizzes,
            "latest_submissions": latest_submissions,
        })

    else:
        # --- STUDENT VIEW DATA ---
        submissions = (
            QuizSubmission.objects
            .filter(user=user)
            .select_related("quiz")
            .order_by("-submitted_at")   # use submitted_at here
        )

        quizzes_taken = submissions.count()
        avg_score = submissions.aggregate(avg=Avg("score"))["avg"]
        latest_submissions = submissions[:5]

        # Suggested quizzes: active quizzes the user hasn't taken yet
        taken_ids = submissions.values_list("quiz_id", flat=True)
        suggested_quizzes = (
            Quiz.objects
            .filter(is_active=True)
            .exclude(id__in=taken_ids)
            .order_by("-created_at")[:5]
        )

        context.update({
            "is_admin": False,
            "quizzes_taken": quizzes_taken,
            "avg_score": avg_score,
            "latest_submissions": latest_submissions,
            "suggested_quizzes": suggested_quizzes,
        })

    return render(request, "dashboard.html", context)


def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # basic admin-only page (you can customize this later or just use dashboard)
    return render(request, 'admin_dashboard.html')


@login_required
def quiz_list_view(request):
    quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'quiz_list.html', {'quizzes': quizzes})


@login_required
@transaction.atomic
def take_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_active=True)
    questions = quiz.questions.prefetch_related('choices')

    if request.method == 'POST':
        # Create submission
        submission = QuizSubmission.objects.create(user=request.user, quiz=quiz)

        total_score = 0
        for question in questions:
            field_name = f"question_{question.id}"
            choice_id = request.POST.get(field_name)
            choice_obj = None
            if choice_id:
                choice_obj = Choice.objects.get(pk=choice_id)
                if choice_obj.is_correct:
                    total_score += question.points

            Answer.objects.create(
                submission=submission,
                question=question,
                selected_choice=choice_obj
            )

        submission.score = total_score
        submission.submitted_at = submission.submitted_at  # usually auto_now_add in model
        submission.save()

        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'submission': submission,
        })

    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_result(request, quiz_id):
    """
    Show the latest submission result for this quiz for the current user.
    Used if you keep a dedicated /quiz/<id>/result/ URL.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    submission = (
        QuizSubmission.objects.filter(user=request.user, quiz=quiz)
        .order_by("-created_at")
        .first()
    )

    if not submission:
        messages.error(request, "No submission found for this quiz.")
        return redirect("take_quiz", quiz_id=quiz.id)

    return render(
        request,
        "quiz_result.html",
        {
            "quiz": quiz,
            "submission": submission,
        },
    )
