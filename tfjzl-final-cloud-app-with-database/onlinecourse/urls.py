from django.urls import path
from . import views

app_name = "onlinecourse"

urlpatterns = [
    # Submit exam answers for a specific course
    path(
        "courses/<int:course_id>/submit/",
        views.submit,
        name="submit",
    ),
    # Show the result of a particular submission
    path(
        "courses/<int:course_id>/submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result",
    ),
    # Additional placeholder routes (e.g., course list, detail) can be added here
]