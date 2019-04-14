from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, resolve_url, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.text import slugify
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, UpdateView, DeleteView,
                                       FormView,)
from django.views.generic.list import ListView
from rest_framework import permissions, viewsets
from .forms import (TermForm, CourseForm, ClassNoteForm, CoursesOfTermForm,
                    UpdateNoteForm, SearchBarForm, CurrentTermForm,)
from .models import Term, Course, ClassNote
from .serializers import TermSerializer, CourseSerializer, ClassNoteSerializer

def SearchBar(request):
    """
    Redirects active-user to a ClassNote object's DetailView given the data that
    they provide to the searchbar. ClassNote objects are retrieved by
    title. If multiple matches are made, user is provided a list of all similar
    hits; refer to NotesListSearchQuery class. If no matches can be made user is
    shown all ClassNote objects.
    """
    redirect_url = reverse_lazy('Notes:notes_list')

    if request.method == 'GET':

        user = request.user
        notes = user.notes.all()

        if notes:
            title = ''.join(request.GET['title'].lower().split(' '))

            matches = []
            for note in notes:
                if title in note.join_title():
                    course = note.course
                    term = course.term
                    args = [term.term_slug, course.course_slug, note.note_slug]
                    redirect_url = reverse_lazy("Notes:one_note", args=args)
                    matches.append(note.note_slug)

            if len(matches) > 1:
                args = ['+'.join(matches)]
                redirect_url = reverse_lazy('Notes:notes_search', args=args)

    return HttpResponseRedirect(redirect_url)

class TermViewSet(viewsets.ModelViewSet):
    """
    Displays the JSON data of all Term objects associated with the active-user.
    """
    serializer_class = TermSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Retrieves all Term objects associated with the active_user; otherwise
        returns an empty queryset for anonymous users.
        """
        active_user = self.request.user
        if active_user.is_authenticated:
            queryset = Term.objects.filter(user=active_user)
        else:
            queryset = Term.objects.none()
        return queryset

class CourseViewSet(viewsets.ModelViewSet):
    """
    Displays JSON data of all Course objects associated with the active-user.
    """
    serializer_class = CourseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Retrieves all Course objects associated with the active_user; otherwise
        returns an empty queryset for anonymous users.
        """
        active_user = self.request.user
        if active_user.is_authenticated:
            queryset = Course.objects.filter(user=active_user)
        else:
            queryset = Course.objects.none()
        return queryset

class ClassNoteViewSet(viewsets.ModelViewSet):
    """
    Displays JSON data of all ClassNote objects associated with the active-user.
    """
    serializer_class = ClassNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """
        Retrieves all ClassNote objects associated with the active_user;
        otherwise returns an empty queryset for anonymous users.
        """
        active_user = self.request.user
        if active_user.is_authenticated:
            queryset = ClassNote.objects.filter(user=active_user)
        else:
            queryset = ClassNote.objects.none()
        return queryset

class CreateTermView(CreateView, ListView):
    """
    Displays form for Term creation and lists all Terms objects related to
    active-user.
    """
    template_name = 'term.html'
    form_class = TermForm
    context_object_name = 'terms'
    success_url = reverse_lazy('Notes:term')

    def form_valid(self, form):
        """
        Creates a new Term object given the valid form.
        """
        term_form = TermForm(self.request.POST)
        term = term_form.save(commit = False)
        term.user = self.request.user
        term.term_slug = slugify(term.session)
        term.save()
        return HttpResponseRedirect(self.success_url)

    def get_queryset(self):
        """
        Retrieves  queryset of all Term objects related to the active-user.
        """
        active_user = self.request.user
        queryset = active_user.terms.all()
        return queryset

class UpdateOptionsTerm(FormView, ListView):
    """
    View for choosing current term, deleting a term, or access the Term object
    update page.
    """
    template_name = 'term_edit_delete.html'
    context_object_name = 'terms'
    form_class = CurrentTermForm
    success_url = reverse_lazy('Notes:term')

    def get_queryset(self):
        """
        Retrieves Term objects related to active user.
        """
        user = self.request.user
        queryset = user.terms.all()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Provides extra context variables in addition to giving the form a more
        sensible context variable name.
        """
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        context['current_term_form'] = context.get('form')
        return context

    def get_terms(self):
        """
        Custom method that retrieves a queryset containing all of the
        active-user's Term objects and produces a list of two-item tuples.
        """
        user = self.request.user
        terms = user.terms.all()
        choices = [('', 'Select current term')]
        choices += [(i, j) for i, j in zip(terms, terms)]
        return choices

    def get_form_kwargs(self):
        """
        Passes the list of two-item tuples returned via the get_terms method to
        the form to be used as selectable choices.
        """
        kwargs = super().get_form_kwargs()
        kwargs['term_choices'] = self.get_terms()
        return kwargs

    def set_current_term(self, current_term):
        """
        Custom method that sets the current attribute of one Term object to
        True, and the rest False. Term objects in question are associated with
        the active-user.
        """
        user = self.request.user
        all_terms = user.terms.all()
        set_term = get_object_or_404(
            Term,
            user=user,
            session=current_term,
            )
        for term in all_terms:
            if term.current == True:
                term.current = False
            elif term == set_term:
                term.current = True
            term.save()

    def form_valid(self, form):
        """
        Form for setting the active-user's current term.
        """
        current_term_form = CurrentTermForm(self.request.POST)
        current_term = form.cleaned_data.get('current_term')
        self.set_current_term(current_term)
        return HttpResponseRedirect(self.success_url)

class UpdateTermView(UpdateView):
    """
    View that displays a form for updating an existing Term object.
    """
    template_name = 'update_term.html'
    form_class = TermForm
    success_url = reverse_lazy('Notes:term_edit')

    def get_object(self):
        """
        Retrieves object to be updated.
        """
        term = get_object_or_404(
        Term,
        term_slug=self.kwargs['slug'],
        user=self.request.user,
        )
        return term

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template for the purpose of turning the
        'edit' button into a 'cancel edit' button.
        """
        context = super().get_context_data(**kwargs)
        context['cancel_edit'] = True
        return context

class DeleteTermView(DeleteView):
    """
    View for deleting an existing Term object.
    """
    success_url = reverse_lazy('Notes:term_edit')

    def get_object(self):
        """
        Retrieves object to be deleted.
        """
        term = get_object_or_404(
            Term,
            term_slug = self.kwargs['slug'],
            user = self.request.user,
            )
        return term

class CreateCourseView(CreateView, ListView):
    """
    View for creating a new Course object and listing all existing Course
    objects.
    """
    template_name = 'course_list.html'
    form_class = CourseForm
    context_object_name = 'courses'
    success_url = reverse_lazy('Notes:course')

    def get_queryset(self):
        """
        Retrieves all Course objects associated with the active-user.
        """
        active_user = self.request.user
        queryset = active_user.courses.all()
        return queryset

    def get_form_kwargs(self):
        """
        Passes the active-user to the form for the purpose of dynamically
        filtering term-choices to those associated with the active-user.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'active_user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """
        Instantiates a new Course object given the valid form.
        """
        course_form = CourseForm(self.request.POST)
        course = course_form.save(commit = False)
        course.user = self.request.user
        course.course_slug = slugify(course.course_code)
        course.save()
        return HttpResponseRedirect(self.success_url)

class CoursesOfTermView(CreateView, ListView):
    """
    View for creating a Course object through a specific term as well as listing
    all Course objects associated with a specific Term object.
    """
    template_name = 'course_list.html'
    context_object_name = 'courses'
    form_class = CoursesOfTermForm

    def get_success_url(self):
        """
        URL that directs user to the courses of a specific term page.
        """
        args = [self.kwargs['slug']]
        return reverse_lazy('Notes:course_term', args = args)

    def get_queryset(self):
        """
        Retrieves Course objects associated with a specific term and the
        active-user.
        """
        user = self.request.user
        term = get_object_or_404(
            Term,
            term_slug = self.kwargs['slug'],
            user = self.request.user,
            )
        slug = term.term_slug
        return Course.objects.filter(user=user,term__term_slug=slug)

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['single_term'] = True
        slug = self.kwargs['slug']
        context['slug'] = slug
        subheader = slug[0].upper() + slug[1::]
        sub_header = ' '.join(subheader.split('-'))
        context['term_name'] = ': ' + sub_header
        return context

    def form_valid(self, form):
        """
        Instantiates a new Course object given the valid form.
        """
        course_form = CoursesOfTermForm(self.request.POST)
        course = course_form.save(commit=False)
        term = get_object_or_404(
            Term,
            term_slug=self.kwargs['slug'],
            user=self.request.user,
            )
        course.term = term
        course.user = self.request.user
        course.course_slug = slugify(course.course_code)
        course.save()
        return HttpResponseRedirect(self.get_success_url())

class UpdateOptionsCourse(ListView):
    """
    View for selecting to edit or delete a specific Course object.
    """
    template_name = 'course_edit_delete.html'
    context_object_name = 'courses'

    def get_queryset(self):
        """
        Retrieves all Course objects associated with the active-user.
        """
        user = self.request.user
        queryset = user.courses.all()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

class DeleteCourseView(DeleteView):
    """
    View for deleting an existing Course object.
    """
    success_url = reverse_lazy('Notes:course_edit')

    def get_object(self):
        """
        Retrieves the object to be deleted.
        """
        course = get_object_or_404(
            Course,
            user = self.request.user,
            course_slug = self.kwargs['slug'],
            )
        return course

    def get_success_url(self):
        """
        Generates the URL that the active-user is redirected to. If a Course
        object is deleted within a specific term, the URL generated will direct
        them to the course page of that aforementioned term; otherwise the URL
        that lists all courses wil be generated.
        """
        referer = self.request.META['HTTP_REFERER'].split('/')
        if referer[-2] == 'Edit':
            return reverse_lazy('Notes:course_edit')
        else:
            url_arg = [self.get_object().term.term_slug]
            return reverse('Notes:course_of_term_edit', args = url_arg)

class CoursesOfTermEditView(ListView):
    """
    View for selecting to edit or delete a Course obejct of a specific term.
    """
    template_name = 'courses_of_term_edit_delete.html'
    context_object_name = 'courses'

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['single_term'] = True
        slug = self.kwargs['slug']
        context['slug'] = slug
        subheader = slug[0].upper() + slug[1::]
        sub_header = ' '.join(subheader.split('-'))
        context['editing'] = True
        context['term_name'] = ': ' + sub_header
        return context

    def get_queryset(self):
        """
        Retrieves all Course ojects associated with the active-user as well as
        a specific Term.
        """
        user = self.request.user
        term = get_object_or_404(
            Term,
            term_slug=self.kwargs['slug'],
            user=user,
            )
        slug = term.term_slug
        return Course.objects.filter(user=user,term__term_slug=slug)

class UpdateCourseView(UpdateView):
    """
    View for updating an existing Course object.
    """
    template_name = 'update_course.html'
    form_class = CourseForm

    def get_object(self):
        """
        Retrieves the object to be updated.
        """
        course = get_object_or_404(
            Course,
            user = self.request.user,
            course_slug = self.kwargs['slug'],
            )
        return course

    def get_success_url(self):
        """
        Generates the URL that the user gets redirected to upon successful
        update. User is either redirected to the page containing all courses
        or the courses of a specific term depending on where they accessed
        the update page.
        """
        referer = self.request.META['HTTP_REFERER'].split('/')
        if referer[-2] == 'SF':
            return reverse_lazy('Notes:course_edit')
        else:
            url_arg = [self.get_object().term.term_slug]
            return reverse('Notes:course_of_term_edit', args=url_arg)

    def get_context_data(self, **kwargs):
        """
        Provides extra context the template.
        """
        context = super().get_context_data(**kwargs)
        context['cancel_edit'] = True
        return context

class CreateNoteView(CreateView):
    """
    View for creating a new ClassNote object.
    """
    template_name = 'notes.html'
    form_class = ClassNoteForm
    success_url = reverse_lazy('Notes:notes_list')

    def get_form_kwargs(self):
        """
        Passes the active-user to the form for the purpose of dynamically
        filtering the course-choices to only those associated with the
        active-user; additionally, should a new ClassNote object be created
        via a specific course page, the course-choices is limited to just
        that specific course.
        """
        form_kwargs = super().get_form_kwargs()
        form_kwargs.update({'active_user': self.request.user})

        try:
            if self.kwargs['course_id']:
                course = Course.objects.filter(course_slug=self.kwargs['course_id'])
                form_kwargs.update({'course': course})
        except KeyError:
            pass
        return form_kwargs

    def form_valid(self, form):
        """
        Instantiates a new ClassNote object given a valid form.
        """
        notes_form = ClassNoteForm(self.request.POST)
        notes = notes_form.save(commit=False)
        user = self.request.user
        notes.user = user
        slug = slugify(notes.title)
        notes.note_slug = slug
        notes.save()
        return HttpResponseRedirect(self.success_url)


class NotesList(ListView):
    """
    View for listing all ClassNote objects.
    """
    template_name = 'notes_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        """
        Retrieves all ClassNote objects associated with the active-user.
        """
        user = self.request.user
        queryset = ClassNote.objects.filter(user=user)
        return queryset

class NotesOfCourse(ListView):
    """
    View for listing all ClassNote objects of a specific course.
    """
    template_name = 'notes_list.html'
    context_object_name = 'notes'

    def get_course(self):
        """
        Custom method that retrieves a specific Course object.
        """
        user = self.request.user
        course = get_object_or_404(
            Course,
            user=user,
            course_slug=self.kwargs['course_id'],
        )
        return course

    def get_context_data(self, **kwargs):
        """
        Provides the template with extra context.
        """
        context = super().get_context_data(**kwargs)
        course = self.get_course()
        term_slug = course.term.term_slug
        course_slug = course.course_slug
        context['term_slug'] = term_slug
        context['course_id'] = course_slug
        context['single_course'] = True
        context['sub_header'] = course.title
        return context

    def get_queryset(self):
        """
        Retrieves all ClassNote objects associated with a specific course and
        the active-user.
        """
        user = self.request.user
        course = self.get_course()
        queryset = ClassNote.objects.filter(user=user, course=course)
        return queryset

class NotesListDashboard(ListView):
    """
    View for listing all ClassNote objects on the dashboard.
    """
    template_name = 'dashboard.html'
    context_object_name = 'notes'

    def get_queryset(self):
        """
        Retrieves all ClassNote objects related to the active-user and orders it
        by most recent.
        """
        user = self.request.user
        queryset = ClassNote.objects.filter(user=user)
        queryset = queryset.order_by('-created_at')
        return queryset

    def get_context_data(self):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data()
        context['dashboard'] = True
        return context

class ReadNote(DetailView):
    """
    View reading an existing ClassNote object.
    """
    template_name = 'notes_list.html'
    context_object_name = 'note'

    def get_object(self):
        """
        Retrieves the ClassNote object to be read.
        """
        note = get_object_or_404(
            ClassNote,
            user=self.request.user,
            note_slug=self.kwargs['note_slug'],
            )
        return note

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['single_note'] = True
        return context

class NoteUpdateOptions(ListView):
    """
    View for selecting whether to update or delete and existing ClassNote
    object.
    """
    template_name = 'notes_edit_delete.html'
    context_object_name = 'notes'

    def get_queryset(self):
        """
        Retrieves all ClassNote objects related to the active-user.
        """
        user = self.request.user
        queryset = ClassNote.objects.filter(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        context['single_course'] = False
        return context

class NotesOfCourseUpdateOptions(ListView):
    """
    View for listing all ClassNote objects of a specific course.
    """
    template_name = 'notes_edit_delete.html'
    context_object_name = 'notes'

    def get_course(self):
        """
        Custom method that retrieves a specific course.
        """
        slug = self.request.META['HTTP_REFERER'].split('/')[-2]
        user = self.request.user
        course = get_object_or_404(
            Course,
            user=user,
            course_slug=slug,
            )
        return course

    def get_queryset(self):
        """
        Retrieves all ClassNote objects associated with the active-user and
        specific course.
        """
        user = self.request.user
        course = self.get_course()
        queryset = user.notes.filter(course=course)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        course = self.get_course()
        term_slug = course.term.term_slug
        course_slug = course.course_slug
        context['term_slug'] = term_slug
        context['course_id'] = course_slug
        context['sub_header'] = course.title
        context['editing'] = True
        context['single_course'] = True
        return context

class DeleteNoteView(DeleteView):
    """
    View for deleting an existing ClassNote object.
    """
    success_url = reverse_lazy('Notes:note_edit')

    def get_object(self):
        """
        Retrieves the ClassNote object to be deleted
        """
        user = self.request.user
        create_date = self.kwargs['created_at']
        object = get_object_or_404(
            ClassNote,
            user = user,
            created_at = create_date,
            )
        return object

class UpdateNoteView(UpdateView):
    """
    View for updating an existing ClassNote object.
    """
    template_name = "note_update.html"
    form_class = UpdateNoteForm
    context_object_name = 'note'

    def get_object(self):
        """
        Retrieves the object to be updated.
        """
        note_slug = self.kwargs['note_slug']
        note = get_object_or_404(
            ClassNote,
            user = self.request.user,
            note_slug = note_slug,
            )
        return note

    def get_success_url(self):
        """
        Generates the URL leading the user back to the ClassNote object's
        DetailView.
        """
        note = self.get_object()
        term_slug = note.course.term.term_slug
        course_slug = note.course.course_slug
        note_slug = note.note_slug
        args = [term_slug, course_slug, note_slug]
        return reverse_lazy('Notes:one_note', args = args)

    def get_context_data(self, **kwargs):
        """
        Provides extra context to the template.
        """
        context = super().get_context_data(**kwargs)
        context['cancel_edit'] = True
        return context

class NotesListSearchQuery(ListView):
    """
    If multiple ClassNote object matches are made from the data the user
    provides to the searchbar, this view will generate a queryset of all those
    objects with similar titles.
    """
    template_name = "notes_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        """
        Generates a queryset of all ClassNote objects that have a title whose
        substring matches what the user provides to the searchbar.
        """
        slugs = self.kwargs['notes_query'].split('+')
        user = self.request.user

        queryset = None
        for slug in slugs:
            if queryset is None:
                queryset = ClassNote.objects.filter(user=user, note_slug=slug)
            else:
                queryset = queryset | ClassNote.objects.filter(
                    user=user,
                    note_slug=slug,
                    )

        if len(queryset) == 0:
            return HttpResponseRedirect(reverse_lazy('Notes:notes_list'))

        return queryset
