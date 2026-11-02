from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Submission,
    Learner,
    Instructor,
)

# ----------------------------------------------------------------------
# Inline definitions
# ----------------------------------------------------------------------
class QuestionInline(admin.StackedInline):
    """Inline for displaying Questions inside a Lesson admin page."""
    model = Question
    extra = 0
    verbose_name = "Question"
    verbose_name_plural = "Questions"


class ChoiceInline(admin.StackedInline):
    """Inline for displaying Choices inside a Question admin page."""
    model = Choice
    extra = 0
    verbose_name = "Choice"
    verbose_name_plural = "Choices"


# ----------------------------------------------------------------------
# Admin model customizations
# ----------------------------------------------------------------------
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin view for Lesson with embedded Question inlines."""
    list_display = ("id", "title", "course")
    search_fields = ("title", "course__name")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin view for Question with embedded Choice inlines."""
    list_display = ("id", "question_text", "lesson")
    search_fields = ("question_text", "lesson__title")
    inlines = [ChoiceInline]


# ----------------------------------------------------------------------
# Register remaining models (default admin)
# ----------------------------------------------------------------------
admin.site.register(Course)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Learner)
admin.site.register(Instructor)