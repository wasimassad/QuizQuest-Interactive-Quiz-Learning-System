from django.contrib import admin
from .models import Profile, Quiz, Question, Choice, QuizSubmission, Answer


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'points')
    inlines = [ChoiceInline]


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'submitted_at')
    list_filter = ('quiz', 'score')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'selected_choice')
