from django import forms
from django.core.exceptions import ValidationError
from models_app.models import Review

# https://docs.djangoproject.com/en/5.2/ref/forms/validation/#validating-fields-with-clean

class Reviewform(forms.ModelForm):
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]

    # Return an int for rating (avoids string/integer confusion later)
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int, #HTML Post will send strings, so convert to int
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Rating: '
    )

    # validation limits
    TITLE_MIN = 5
    TITLE_MAX = 100
    COMMENT_MIN = 10
    COMMENT_MAX = 2000

    def __init__(self, *args, **kwargs):
        # allow the view to pass order_item and user for duplicate-checking
        self.order_item = kwargs.pop('order_item', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Review
        fields = ['title', 'comment', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter a review title',
                'class': 'form-control',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Share your experience',
                'rows': 4,
                'class': 'form-control',
            })
        }

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()
        if len(title) < self.TITLE_MIN:
            #displays an error message if title is too short
            raise ValidationError(f'Title must be at least {self.TITLE_MIN} characters long.') 
        if len(title) > self.TITLE_MAX:
            #displays an error message if title is too long
            raise ValidationError(f'Title may not exceed {self.TITLE_MAX} characters.')
        return title

    def clean_comment(self):
        comment = (self.cleaned_data.get('comment') or '').strip()
        if len(comment) < self.COMMENT_MIN:
            #displays an error message if comment is too short
            raise ValidationError(f'Please provide a longer review (at least {self.COMMENT_MIN} characters).')
        if len(comment) > self.COMMENT_MAX:
            #displays an error message if comment is too long
            raise ValidationError(f'Review is too long (maximum {self.COMMENT_MAX} characters).')
        return comment

    def clean(self):
        cleaned = super().clean()

        # Prevent a duplicate review for the same order_item
        if self.order_item and not self.instance.pk: #if order item is provided and this is a new review
            if Review.objects.filter(order_item=self.order_item).exists():
                raise ValidationError('You have already submitted a review for this order item.')

        return cleaned