from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory, modelformset_factory, BaseModelFormSet
from .models import House, Photo, Question, Video, Prompt
from django.utils.safestring import SafeString

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['photo']


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['house_name', 'address', 'house_number']


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['video']


def create_custom_formset(parent_model, child_model, form, **kwargs):
    ModelFormSet = inlineformset_factory(parent_model, child_model, 
                                         form=form, 
                                         can_delete=True, 
                                         can_delete_extra=False, **kwargs)
    class CustomModelFormSet(ModelFormSet):
        def save(self, user, house=None, commit=True):
            forms = super().save(commit=False)
            for form in forms:
                form.user = user
                if house is not None:
                    form.house = house
                if commit:
                    form.save()
            return forms
    return CustomModelFormSet

    
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'answer_text', 'house', 'question_number']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['house'].queryset = House.objects.filter(user=user)

PhotoFormSet = modelformset_factory(Photo, form=PhotoForm, can_delete=True, can_delete_extra=False)
VideoFormSet = modelformset_factory(Video, form=VideoForm, can_delete=True, can_delete_extra=False)


class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ['helper_text', 'prompt']
        widgets = {
            'helper_text': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'helper-text-widget'}),
            'prompt': forms.Textarea(attrs={'class': 'textarea-widget', 'oninput': 'autoResize(this)'}),
        }

class PromptFormAdmin(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ['prompt_name', 'prompt', 'helper_text']
        widgets = {
            'prompt': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
        }

class BasePromptFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.queryset = Prompt.objects.filter(user=user)



PromptFormSet = modelformset_factory(Prompt, form=PromptForm, formset=BasePromptFormSet, extra=0, edit_only=True)

class NewsletterForm(forms.Form):
    text_field = forms.CharField(
        label="Newsletter text", 
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your text here',
            'cols': 50,
            'rows': 10,
        })
    )
