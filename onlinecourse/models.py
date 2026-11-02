from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    """Course model representing an online course."""
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """Lesson model belonging to a Course."""
    course = models.ForeignKey(
        Course, related_name="lessons", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Question(models.Model):
    """
    Question model used in exams.
    Includes a ``grade`` field indicating the points for the question
    and an ``is_get_score`` method to evaluate a selected choice.
    """
    lesson = models.ForeignKey(
        Lesson, related_name="questions", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=500)
    grade = models.PositiveIntegerField(default=1)  # points awarded for a correct answer

    def __str__(self):
        return f"Q: {self.text[:50]}..."

    def is_get_score(self, selected_choice):
        """
        Return ``True`` if the provided ``selected_choice`` is the correct answer
        for this question.
        """
        return selected_choice.is_correct


class Choice(models.Model):
    """Possible answer for a Question."""
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class Learner(models.Model):
    """Learner profile linked to Django's built‑in User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Submission(models.Model):
    """
    Stores a learner's attempt at a course exam.
    The ``calculate_score`` method aggregates points from correctly answered
    choices using the ``grade`` field of each Question.
    """
    learner = models.ForeignKey(
        Learner, related_name="submissions", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course, related_name="submissions", on_delete=models.CASCADE
    )
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner} - {self.course.name} - {self.score} pts"

    def calculate_score(self):
        """Calculate total score based on correct choices."""
        total = 0
        for answer in self.answers.select_related("choice__question").all():
            if answer.choice.is_correct:
                total += answer.choice.question.grade
        self.score = total
        self.save()


class Answer(models.Model):
    """Link a selected Choice to a Submission."""
    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE
    )
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"Answer for {self.submission}"