from django.contrib.auth import forms, get_user_model, models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Term, Course, ClassNote

class TermForm(forms.ModelForm):
    """
    Form for creating a new Term object.
    """
    fields = ('school', 'year', 'session')

    def __init__(self, *args, **kwargs):
        """
        HTML widget modification.
        """
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].label = ''

        placeholders = (
            'School name', 'Academic year (numerical value)', 'Academic term'
            )

        for field, placeholder in zip(self.fields, placeholders):
            self.fields[field].widget.attrs.update({'placeholder': placeholder})

    class Meta():
        """
        Fields of the Term model to appear on the form.
        """
        model = Term
        fields = ('school', 'year', 'session')

class CourseForm(forms.ModelForm):
    """
    Form for creating a new Course object.
    """
    fields = ('title', 'course_code', 'term')

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters the term-choices available to the user when
        associating a course with a term; insofar as the terms available are
        those associated with the user.
        """
        user = kwargs.pop('active_user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['term'].queryset = Term.objects.filter(user=user)

        for field in self.fields:
            self.fields[field].label = ''

        placeholders = ('Course title', 'Course code')

        for field, placeholder in zip(self.fields, placeholders):
            self.fields[field].widget.attrs.update({'placeholder': placeholder})

        self.fields['term'].empty_label = 'Academic term'

    class Meta():
        """
        Fields of the Course model to appear on the form.
        """
        model = Course
        fields = ('title', 'course_code', 'term')

class CoursesOfTermForm(forms.ModelForm):
    """
    Form for creating a new Course object accessed from a specific term.
    """
    fields = ('title', 'course_code')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].label = ''

        placeholders = ('Course title', 'Course code')

        for field, placeholder in zip(self.fields, placeholders):
            self.fields[field].widget.attrs.update({'placeholder': placeholder})

    class Meta():
        """
        Fields of the Course model to appear on the form.
        """
        model = Course
        fields = ('title', 'course_code')

class ClassNoteForm(forms.ModelForm):
    """
    Form for creating a new ClassNote object; that is, the actual note.
    """
    fields = ('title', 'body', 'course')

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters course-choices by limiting them to only those
        associated with the user, in addition to limiting the course-choice to
        just one option should the user create a new note through a specific
        course.
        """
        user = kwargs.pop('active_user', None)
        current_course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].label = ''

        self.fields['course'].widget.attrs.update({"class": "w-10"})
        self.fields['title'].widget.attrs.update(
            {"placeholder": "Please enter a title"}
            )
        self.fields['course'].empty_label = 'Select a course'

        if user is not None:
            self.fields['course'].queryset = Course.objects.filter(user=user)

            if current_course is not None:
                self.fields['course'].queryset = current_course

    class Meta():
        """
        Fields of the ClassNote model to appear on form.
        """
        model = ClassNote
        fields = ('title', 'body', 'course')

class UpdateNoteForm(forms.ModelForm):
    """
    Form for updating an existing ClassNote object.
    """
    fields = ('title', 'body', 'course')

    def __init__(self, *args, **kwargs):
        """
        HTML widget modification.
        """
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].label = ''

        self.fields['course'].widget.attrs.update({"class": "w-10"})
        self.fields['title'].widget.attrs.update(
            {"placeholder": "Please enter a title"}
            )
        self.fields['course'].empty_label = 'Select a course'

    class Meta():
        """
        Fields of a ClassNote object that a user can update.
        """
        model = ClassNote
        fields = ('title', 'body', 'course')

class CurrentTermForm(forms.Form):
    """
    Form that allows user to select a current term.
    """
    current_term = forms.ChoiceField()

    def __init__(self, term_choices, *args, **kwargs):
        """
        HTML widget modification and initializes form with term-choices it
        receives from the associated view's form_kwargs.
        """
        super().__init__(*args, **kwargs)
        self.fields['current_term'].label = ''
        self.fields['current_term'].choices = term_choices

class SearchBarForm(forms.ModelForm):
    """
    Searchbar that allows users to look for a specific note by note-title.
    """

    def __init__(self, *args, **kwargs):
        """
        HTML widget modification
        """
        super().__init__(*args, **kwargs)
        searchbar_styles = {
            "class": "form-control form-control-dark w-100",
            "placeholder": "Enter note title",
            "aria-label": "Search",
            }
        self.fields['title'].widget.attrs.update(searchbar_styles)
        self.fields['title'].label = ''

    class Meta():
        """
        Allows user to search for a specific note by its title.
        """
        model = ClassNote
        fields = ('title',)
