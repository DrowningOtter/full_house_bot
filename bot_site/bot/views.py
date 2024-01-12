import json
from typing import Any
from django.db.models.query import QuerySet
from django.forms import inlineformset_factory, modelformset_factory
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import get_object_or_404
from django.db import connection as db_connection
from django.http import HttpResponseServerError

from .models import House, Question, Photo, Video, Prompt
from .forms import (PhotoForm, HouseForm, QuestionForm, 
                    VideoForm, create_custom_formset, 
                    PhotoFormSet, VideoFormSet, PromptForm,
                    PromptFormSet, NewsletterForm)

from pika import BlockingConnection, URLParameters
from bot_management.conf import RABBITMQ_LOGIN, RABBITMQ_PASSWORD, RABBITMQ_QUEUE_NAME, RABBITMQ_HOST_NAME

@login_required
def index(request):
    # Home page, should redirect to login if user is not authenticated
    # else show some page like "Hello, very happy to see you"
    return render(request, "bot/index.html")


class HouseAccessMixin(UserPassesTestMixin):
    def test_func(self):
        house = get_object_or_404(House, pk=self.kwargs['pk'])
        return self.request.user == house.user


class HouseDetailView(LoginRequiredMixin, HouseAccessMixin, generic.DetailView):
    model = House

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)


class HouseListView(LoginRequiredMixin, generic.ListView):
    model = House

    def get_queryset(self):
        return House.objects.filter(user=self.request.user).order_by('house_number')
    

class QuestionAccessMixin(UserPassesTestMixin):
    def test_func(self):
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        return self.request.user == question.user
    

class QuestionDetailView(LoginRequiredMixin, QuestionAccessMixin, generic.DetailView):
    model = Question

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user)
    

class QuestionListView(LoginRequiredMixin, generic.ListView):
    model = Question

    def get_queryset(self):
        return Question.objects.filter(user=self.request.user).order_by('question_number')


class PhotosListView(LoginRequiredMixin, generic.ListView):
    model = Photo

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)
    

class VideosListView(LoginRequiredMixin, generic.ListView):
    model = Video

    def get_queryset(self):
        return Video.objects.filter(user=self.request.user)

class HouseCreate(LoginRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    
    def get_context_data(self, **kwargs):
        ctx = super(HouseCreate, self).get_context_data(**kwargs)
        ctx['photos'] = create_custom_formset(House, Photo, PhotoForm, fields=['photo'])() if 'photos' not in kwargs else kwargs['photos']
        return ctx
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        photoformset = create_custom_formset(House, Photo, PhotoForm)(self.request.POST, self.request.FILES)
        if form.is_valid() and photoformset.is_valid():
            return self.form_valid(form, photoformset)
        else:
            return self.form_invalid(form, photoformset)
        
    def form_valid(self, form, photoformset):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        form.save()
        photoformset.save(self.request.user, self.object)
        return redirect(reverse('bot:house-detail', args=[self.object.id]))
    
    def form_invalid(self, form, photoformset):
        return self.render_to_response(
            self.get_context_data(form=form, photos=photoformset)
        )
    

class HouseUpdate(LoginRequiredMixin, HouseAccessMixin, UpdateView):
    model = House
    form_class = HouseForm

    def get_context_data(self, **kwargs):
        ctx = super(HouseUpdate, self).get_context_data(**kwargs)
        ctx['photos'] = create_custom_formset(House, Photo, PhotoForm, fields=['photo'])(instance=self.object)
        return ctx
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        photoformset = create_custom_formset(House, Photo, PhotoForm)(
            self.request.POST, 
            self.request.FILES,
            instance=self.object)
        if form.is_valid() and photoformset.is_valid():
            return self.form_valid(form, photoformset)
        else:
            return self.form_invalid(form, photoformset)
        
    def form_valid(self, form, photoformset):
        form.save()
        for deleted_form in photoformset.deleted_forms:
            deleted_form.instance.delete()
        photoformset.save(self.request.user, self.object)
        return redirect(reverse('bot:house-detail', args=[self.object.id]))
    
    def form_invalid(self, form, photoformset):
        return self.render_to_response(
            self.get_context_data(form=form, photos=photoformset)
        )



class HouseDelete(LoginRequiredMixin, HouseAccessMixin, DeleteView):
    model = House
    success_url = reverse_lazy('bot:houses')

    def form_valid(self, form):
        try:
            self.object.delete()
            return redirect(self.success_url)
        except Exception as ex:
            return redirect(reverse("bot:house-delete", kwargs={"pk": self.object.pk}))



class QuestionCreate(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photos'] = PhotoFormSet(queryset=Photo.objects.none()) if 'photos' not in kwargs else kwargs['photos']
        ctx['videos'] = VideoFormSet(queryset=Video.objects.none()) if 'videos' not in kwargs else kwargs['videos']
        return ctx
    
    def post(self, request, *args, **kwargs):   
        photoformset = PhotoFormSet(self.request.POST, self.request.FILES, queryset=Photo.objects.none())
        videoformset = VideoFormSet(self.request.POST, self.request.FILES, queryset=Video.objects.none())
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid() and photoformset.is_valid() and videoformset.is_valid():
            return self.form_valid(form, photoformset, videoformset)
        else:
            return self.form_invalid(form, photoformset, videoformset)
        
    def form_valid(self, form, photoformset, videoformset):
        question = form.save(commit=False)
        question.user = self.request.user
        question.save()
        photos = photoformset.save(commit=False)
        videos = videoformset.save(commit=False)
        for photo in photos:
            photo.user = self.request.user
            photo.question = question
            photo.save()
        for video in videos:
            video.user = self.request.user
            video.question = question
            video.save()
        question.save()
        return redirect(reverse('bot:question-detail', args=[str(question.id)]))
    
    def form_invalid(self, form, photoformset, videoformset):
        return self.render_to_response(
            self.get_context_data(form=form, photos=photoformset, videos=videoformset)
        )


class QuestionUpdate(LoginRequiredMixin, QuestionAccessMixin, UpdateView):
    model = Question
    form_class = QuestionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # ctx['photos'] = PhotoFormSet(instance=self.object)
        ctx['photos'] = inlineformset_factory(Question, Photo, form=PhotoForm, fields=['photo'], can_delete_extra=False)(instance=self.object)
        # ctx['videos'] = VideoFormSet(instance=self.object)
        ctx['videos'] = inlineformset_factory(Question, Video, form=VideoForm, fields=['video'], can_delete_extra=False)(instance=self.object)
        return ctx
    
    def post(self, requset, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # photoformset = PhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        photoformset = inlineformset_factory(Question, Photo, form=PhotoForm, fields=['photo'], can_delete_extra=False)(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        # videoformset = VideoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        videoformset = inlineformset_factory(Question, Video, form=VideoForm, fields=['video'], can_delete_extra=False)(
            self.request.POST,
            self.request.FILES,
            instance=self.object
        )
        if form.is_valid() and photoformset.is_valid() and videoformset.is_valid():
            return self.form_valid(form, photoformset, videoformset)
        else:
            return self.form_invalid(form, photoformset, videoformset)
        
    def form_valid(self, form, photoformset, videoformset):
        form.save()
        # photos = photoformset.save(commit=False)
        for deleted_photos in photoformset.deleted_forms:
            deleted_photos.instance.delete()
        # videos = videoformset.save(commit=False)
        for deleted_videos in videoformset.deleted_forms:
            deleted_videos.instance.delete()

        photos = photoformset.save(commit=False)
        for photo in photos:
            photo.question = self.object
            photo.user = self.request.user
            photo.save()
        videos = videoformset.save(commit=False)
        for video in videos:
            video.question = self.object
            video.user = self.request.user
            video.save()
        return redirect(reverse('bot:question-detail', args=[self.object.id]))

    def form_invalid(self, form, photoformset, videoformset):
        return self.render_to_response(
            self.get_context_data(form=form, photos=photoformset, videos=videoformset)
        )


class QuestionDelete(LoginRequiredMixin, QuestionAccessMixin, DeleteView):
    model = Question
    success_url = reverse_lazy('bot:questions')

    def form_valid(self, form):
        try:
            self.object.delete()
            return redirect(self.success_url)
        except Exception as ex:
            return redirect(reverse("bot:question-delete", kwargs={"pk": self.object.pk}))



class HouseDelete(LoginRequiredMixin, HouseAccessMixin, DeleteView):
    model = House
    success_url = reverse_lazy('bot:houses')

    def form_valid(self, form):
        try:
            self.object.delete()
            return redirect(self.success_url)
        except Exception as ex:
            return redirect(reverse("bot:house-delete", kwargs={"pk": self.object.pk}))


@login_required
def update_prompts(request):
    if request.method == "POST":
        formset = PromptFormSet(request.POST, user=request.user)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('bot:prompts-update'))
    else:
        formset = PromptFormSet(user=request.user)
    return render(request, "bot/prompt_form.html", {'formset': formset})


@login_required
def send_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            text_value = form.cleaned_data['text_field']
            print('DEBUG\n', text_value)
            with db_connection.cursor() as cursor:
                cursor.execute(f"""SELECT tg_user_id FROM bot_registeredusers WHERE user_id = {request.user.id}""")
                user_list = [item[0] for item in cursor.fetchall()]
            # отправить сообщение в тг
            connection = BlockingConnection(URLParameters(f"amqp://{RABBITMQ_LOGIN}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_NAME}/"))
            channel = connection.channel()
            queue_name = RABBITMQ_QUEUE_NAME + str(request.user.id)
            print("DEBUG: queue_name=", queue_name)
            try:
                queue = channel.queue_declare(queue_name, passive=True)
            except ValueError:
                return HttpResponseServerError("Internal Server Error: Something went wrong.")
            data = { "user_list": user_list, "newsletter_text": text_value }
            message_body = json.dumps(data)
            channel.basic_publish(
                # pika.Message(body=message_body.encode("utf-8")),
                exchange="amq.direct",
                body=message_body.encode("utf-8"),
                routing_key=queue_name,
            )
            connection.close()
    else:
        form = NewsletterForm()
    return render(request, "bot/newsletter_form.html", {'form': form})