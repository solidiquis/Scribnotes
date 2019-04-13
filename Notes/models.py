from ckeditor.fields import RichTextField
from django.db import models
from django.contrib import auth
from django.contrib.auth import get_user_model

class Term(models.Model):
    """
    Model whose primary purpose is to display user's academic session, school,
    and year; each term object is related to a specific user.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='terms',
        )
    school = models.CharField(max_length=40, blank=False)
    year = models.IntegerField(blank=False, null=True)
    session = models.CharField(max_length=40, blank=False)
    term_slug = models.SlugField(null=True)
    current = models.BooleanField(default=False)

    def __str__(self):
        """
        Provides a readable string representation of Term object
        """
        return f'{self.session}'

    class Meta():
        """
        Arranges queryset by increasing year.
        """
        ordering = ['-year']

class Course(models.Model):
    """
    Model that stores information about user's academic course. Each course
    object is related to a specific user and term.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='courses',
        )
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        null=True,
        related_name='courses'
        )
    course_code = models.CharField(
        max_length=40,
        unique=True,
        blank=False,
        )
    title = models.CharField(max_length=40, blank=False)
    course_slug = models.SlugField(null=True)


    def __str__(self):
        """
        Provides a readable string representation of Course object.
        """
        return f'{self.course_code}'

    class Meta():
        """
        Orders courses alphabetically by their course code.
        """
        ordering = ['course_code']

class ClassNote(models.Model):
    """
    Model whose objects are the actual notes that the user takes. Each ClassNote
    object is related to a specific user their course.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='notes',
        )
    title = models.CharField(max_length=47, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    body = RichTextField(config_name='ckeditor')
    note_slug = models.SlugField(null=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        related_name='notes'
        )

    def __str__(self):
        """
        Provides a readable string representation of ClassNote object.
        """
        return f'{self.title}'

    def join_title(self):
        """
        Uses a ClassNote object's title to produce a lowercased version devoid
        of whitespaces and returns it as a string.
        """
        joined_title = ''.join(self.title.lower().split(' '))
        return joined_title

    class Meta():
        """
        Orders ClassNote objects first, by their courses alphabetically; objects
        with the same course are then ordered by most recent.
        """
        ordering = ['course', '-created_at']
