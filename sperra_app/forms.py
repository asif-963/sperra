from django import forms
from django.forms import inlineformset_factory
from .models import (
    Blog,TeamMember,Testimonial,Category,GalleryImage,
    Treatments,TreatmentFAQ,ContactMessage
    
)



# --------- Blog Form ---------
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["image", "title", "description"]

# -------------Team Form ---------
class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ["name", "profession", "image", "linkedin", "facebook", "instagram"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False

#----------Testimonial-------------
class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "image", "review"]

#----------Gallery----------------
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class GalleryImageForm(forms.ModelForm):  # no need
    class Meta:
        model = GalleryImage
        fields = ["category", "title", "image"]

# --------- Treatment Form ---------
class TreatmentsForm(forms.ModelForm):
    class Meta:
        model = Treatments
        fields = ["image", "title", "description"]


TreatmentFAQFormSet = inlineformset_factory(
    Treatments,
    TreatmentFAQ,
    fields=("question", "answer"),
    extra=1,
    can_delete=True
)

#----------ContactForm---------------
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name","last_name","phone","message",]