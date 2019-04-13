from rest_framework import serializers
from .models import Term, Course, ClassNote

class TermSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes and deserializes Term instances into representations such as
    JSON.
    """

    class Meta():
        """
        Fields of Term instances that will get serialized/deserialized.
        """
        model = Term
        fields = ('school', 'year', 'session', 'term_slug',)

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes and deserializes Course instances into representations such as
    JSON.
    """

    class Meta():
        """
        Fields of Term instances that will get serialized/deserialized.
        """
        model = Course
        fields = ('title', 'course_code', 'course_slug', 'term',)

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters term choices by limiting options to the terms
        related to the active user via foreign-key.
        """
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if user.is_authenticated:
            self.fields['term'].queryset = Term.objects.filter(user=user)
        else:
            self.fields['term'].queryset = Term.objects.none()

class ClassNoteSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes and deserializes ClassNote instances into representations such as
    JSON.
    """

    class Meta():
        """
        Fields of ClassNote instances that will get serialized/deserialized.
        """
        model = ClassNote
        fields = ('title', 'body', 'note_slug', 'course',)

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters course choices by limiting options to the courses
        related to the active user via foreign-key.
        """
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if user.is_authenticated:
            self.fields['course'].queryset = Course.objects.filter(user=user)
        else:
            self.fields['course'].queryset = Course.objects.none()
