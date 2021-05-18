from django.conf.urls import handler404, handler500
from django.urls import path

from . import views

handler404 = "posts.views.page_not_found"
handler500 = "posts.views.server_error" 

urlpatterns = [
    path('', views.index, name='index'),
    path('group/', views.group_index, name='group_index'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.new_post, name='new_post'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path("<username>/<int:post_id>/comment", views.add_comment,
         name="add_comment"),
]
