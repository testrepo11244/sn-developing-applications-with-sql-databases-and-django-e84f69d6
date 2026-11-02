from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.


class Instructor(models.Model):
    """An instructor who teaches one or more courses."""
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    """A learner who can enroll in one or more courses."""
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT,
    )
    social_link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.occupation


class Course(models.Model):
    """An online course made up of lessons and exam questions."""
    name = models.CharField(null=False, max_length=100, default='online Course')
    description = models.CharField(max_length=1000)
    # A course can have many instructors and an instructor can teach many courses.
    instructors = models.ManyToManyField(Instructor)
    # A course can have many learners and a learner can enroll in many courses.
    learners = models.ManyToManyField(Learner, through='Enrollment')

    def __str__(self):
        return 'Course: ' + self.name


class Lesson(models.Model):
    """A lesson that belongs to a course."""
    title = models.CharField(null=False, max_length=30, default='Lesson Title')
    course = models.ForeignKey(
        Course,
        null=False,
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    content = models.TextField()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """An enrollment of a learner in a course (through model)."""
    AUDIT = 'audit'
    HONOR = 'honor'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
    ]
    course = models.ForeignKey(
        Course,
        null=False,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    learner = models.ForeignKey(
        Learner,
        null=False,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    date_enrolled = models.DateField(default=now, null=True)
    mode = models.CharField(
        null=False,
        max_length=5,
        choices=COURSE_MODES,
        default=AUDIT,
    )
    rating = models.FloatField(null=True)

    def __str__(self):
        return 'Enrollment: ' + self.learner.user.username + ' - ' + self.course.name


class Question(models.Model):
    """An exam question that belongs to a course."""
    # Each question belongs to exactly one course.
    # Deleting a course deletes all of its questions.
    course = models.ForeignKey(
        Course,
        null=False,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_text = models.CharField(null=False, max_length=255)
    # Points awarded when the question is answered correctly.
    grade = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    """A possible answer for a question."""
    # Each choice belongs to exactly one question.
    # Deleting a question deletes all of its choices.
    question = models.ForeignKey(
        Question,
        null=False,
        on_delete=models.CASCADE,
        related_name='choices',
    )
    choice_text = models.CharField(null=False, max_length=255)
    # True when this choice is a correct answer for its question.
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    """A learner's submitted answers for a course exam."""
    # Each submission is tied to exactly one enrollment.
    # Deleting an enrollment deletes all of its submissions.
    enrollment = models.ForeignKey(
        Enrollment,
        null=False,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    # A submission contains the choices selected by the learner, and a
    # choice can be selected in many submissions.
    choices = models.ManyToManyField(Choice)
    # Total score earned by this submission.
    grade = models.IntegerField(null=False, default=0)

    def __str__(self):
        return 'Submission ' + str(self.id) + ' for ' + self.enrollment.course.name