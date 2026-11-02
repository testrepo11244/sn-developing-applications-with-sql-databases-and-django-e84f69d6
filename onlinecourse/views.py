from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import (
    Course,
    Lesson,
    Learner,
    Enrollment,
    Question,
    Choice,
    Submission,
)


def course_list(request):
    """Show all available online courses."""
    courses = Course.objects.all()
    return render(
        request,
        'onlinecourse/course_list_bootstrap.html',
        {'courses': courses},
    )


def course_details(request, course_id):
    """Show the details of one course and all of its lessons."""
    course = get_object_or_404(Course, pk=course_id)
    lessons = Lesson.objects.filter(course=course)
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(
            course=course,
            learner__user=request.user,
        ).exists()
    return render(
        request,
        'onlinecourse/course_details_bootstrap.html',
        {
            'course': course,
            'lessons': lessons,
            'enrolled': enrolled,
        },
    )


@login_required
def enroll(request, course_id):
    """Enroll the current learner in the given course."""
    course = get_object_or_404(Course, pk=course_id)
    learner = Learner.objects.get(user=request.user)
    Enrollment.objects.create(
        course=course,
        learner=learner,
        mode=Enrollment.HONOR,
    )
    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:course_details', args=(course.id,))
    )


def extract_answers(request):
    """Extract the selected choice ids from the submitted exam form."""
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            try:
                choice_id = int(value)
            except (TypeError, ValueError):
                continue
            submitted_answers.append(choice_id)
    return submitted_answers


def calculate_grade(submission):
    """Grade the submission, question by question."""
    selected_choices = submission.choices.all()
    questions = Question.objects.filter(
        course=submission.enrollment.course,
    ).prefetch_related('choices')
    grade = 0
    for question in questions:
        correct_ids = set(
            question.choices.filter(is_correct=True).values_list('id', flat=True)
        )
        selected_ids = set(
            selected_choices.filter(question=question).values_list('id', flat=True)
        )
        if correct_ids and selected_ids == correct_ids:
            grade += question.grade
    return grade


@login_required
def submit(request, course_id):
    """
    Submit the selected answers for the exam of the given course.

    Steps:
    1. Get the current user and the course object.
    2. Get the enrollment of the current user for the course.
    3. Create a submission referring to the enrollment.
    4. Add the selected choices to the submission.
    5. Grade the submission and save it.
    6. Redirect to the exam result page.
    """
    # 1. Get the current user and the course object
    user = request.user
    course = get_object_or_404(Course, pk=course_id)

    # 2. Get the enrollment of the current user (learner) for this course
    enrollment = get_object_or_404(Enrollment, learner__user=user, course=course)

    # 3. Create a submission object referring to the enrollment
    submission = Submission.objects.create(enrollment=enrollment)

    # 4. Add the selected choices to the submission object
    choices = extract_answers(request)
    submission.choices.set(choices)

    # 5. Grade the submission and save it
    submission.grade = calculate_grade(submission)
    submission.save()

    # 6. Redirect to the exam result page
    return HttpResponseRedirect(
        reverse(
            viewname='onlinecourse:show_exam_result',
            args=(course.id, submission.id),
        )
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    """
    Show the exam result page for the given course and submission.

    Steps:
    1. Get the course and the submission objects.
    2. Get the enrollment related to the submission.
    3. Get all questions of the course with their choices.
    4. Get the ids of the choices selected in this submission.
    5. Render the exam result template with the context.
    """
    # 1. Get the course and the submission objects
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # 2. Get the enrollment related to the submission
    enrollment = submission.enrollment

    # 3. Get all questions of the course with their choices
    questions = Question.objects.filter(course=course).prefetch_related('choices')

    # 4. Get the ids of the choices selected in this submission
    selected_ids = list(submission.choices.values_list('id', flat=True))

    # Total possible score for the exam
    total_grade = sum(question.grade for question in questions)

    # 5. Render the exam result template with the context
    context = {
        'course': course,
        'enrollment': enrollment,
        'submission': submission,
        'questions': questions,
        'selected_ids': selected_ids,
        'grade': submission.grade,
        'total_grade': total_grade,
        'passed': total_grade > 0 and submission.grade >= total_grade,
    }
    return render(request, 'onlinecourse/exam_result.html', context)