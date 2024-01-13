from django.contrib import admin

from .models import Photo, Video, House, Question, Prompt, AccessInfo, RegisteredUsers
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class RegisteredUsersInline(admin.TabularInline):
    model = RegisteredUsers

class HouseAdmin(admin.ModelAdmin):
    list_display = ['id', 'house_number', 'house_name', 'address', 'user']
    list_filter = ['user']
    inlines = [PhotoInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text', 'user', 'get_house']
    list_filter = ['user']

    inlines = [PhotoInline, VideoInline]

    def get_house(self, obj):
        return obj.house.house_name if obj.house else '-'
    get_house.short_description = 'House'

class PhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo', 'house', 'question']


class PromptAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt_name', 'prompt', 'user_id']


class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'is_staff']
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    readonly_fields = ()
    inlines = [RegisteredUsersInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Video)
admin.site.register(House, HouseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Prompt, PromptAdmin)
admin.site.register(AccessInfo)
admin.site.register(RegisteredUsers)