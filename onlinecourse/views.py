from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Course, Lesson, Question, Choice, Submission, Learner, Instructor
from django.http import HttpResponseBadRequest


def submit(request, course_id):
    """
    Handles the POST request when a learner submits answers for a course exam.
    It creates a Submission instance, attaches the selected Choice objects,
    and redirects to the result view.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed.")

    course = get_object_or_404(Course, pk=course_id)

    # In a real app we would verify the learner is enrolled; here we assume a learner exists.
    learner = Learner.objects.first()
    if not learner:
        return HttpResponseBadRequest("No learner found for submission.")

    # Create a new submission record
    submission = Submission.objects.create(
        learner=learner,
        course=course,
    )

    # Expecting POST data in the form: choice_<question_id> = <choice_id>
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                question_id = int(key.split("_")[1])
                choice_id = int(value)
                question = Question.objects.get(pk=question_id)
                choice = Choice.objects.get(pk=choice_id, question=question)
                submission.choices.add(choice)
            except (ValueError, Question.DoesNotExist, Choice.DoesNotExist):
                # Skip malformed entries
                continue

    submission.save()

    # Redirect to the result page
    return redirect(
        reverse(
            "show_exam_result",
            kwargs={"course_id": course.id, "submission_id": submission.id},
        )
    )


def show_exam_result(request, course_id, submission_id):
    """
    Displays the exam result for a given submission.
    Calculates the score, determines pass/fail, and renders a template.
    """
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id, course=course)

    # Gather all questions for the course (through lessons)
    questions = Question.objects.filter(lesson__course=course).distinct()
    total_questions = questions.count()

    # Determine how many selected choices are correct
    correct_choices = Choice.objects.filter(
        question__in=questions, is_correct=True, submissions=submission
    ).distinct()
    correct_answers = correct_choices.count()

    # Calculate percentage score
    score_percent = (
        (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    )

    # Define passing threshold (e.g., 70%)
    passing_threshold = 70
    is_passed = score_percent >= passing_threshold

    context = {
        "course": course,
        "submission": submission,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percent": round(score_percent, 2),
        "is_passed": is_passed,
        "passing_threshold": passing_threshold,
    }

    return render(request, "onlinecourse/exam_result.html", context)