from django.urls import path
from . import views
 
app_name = "bot"
urlpatterns = [
    path('', views.index, name='index'),

    path('houses/', views.HouseListView.as_view(), name='houses'),
    path('house/<int:pk>/', views.HouseDetailView.as_view(), name='house-detail'),
    path('questions/', views.QuestionListView.as_view(), name='questions'),
    path('question/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),

    path('house/create/', views.HouseCreate.as_view(), name='house-create'),
    path('house/<int:pk>/update/', views.HouseUpdate.as_view(), name='house-update'),
    path('house/<int:pk>/delete/', views.HouseDelete.as_view(), name='house-delete'),

    path('question/create/', views.QuestionCreate.as_view(), name='question-create'),
    path('question/<int:pk>/update/', views.QuestionUpdate.as_view(), name='question-update'),
    path('question/<int:pk>/delete/', views.QuestionDelete.as_view(), name='question-delete'),

    path('photos/', views.PhotosListView.as_view(), name='photos'),
    path('videos/', views.VideosListView.as_view(), name='videos'),

    path('prompts/', views.update_prompts, name='prompts-update'),
    path('newsletter/', views.send_newsletter, name='newsletter'),

    #DEBUG, SHOULD REMOVE!!!
    path('create_queue', views.create_queue),
]