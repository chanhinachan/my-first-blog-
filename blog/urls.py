from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),
    path('post/<int:pk>/remove/', views.post_remove, name='post_remove'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('post/tag/<str:tag_name>/', views.post_tag, name='post_tag'),
    path('tagcreate/', views.tag_create, name='tag_create'),
    path('tagremove/<str:tag_name>/remove', views.tag_remove, name='tag_remove'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('register', views.AccountRegistration.as_view(), name='register'),
    path('post2/new/', views.post_new_2, name='post_new_2'),
    path('post2/<int:pk>/edit/', views.post_edit_2, name='post_edit_2'),
    path('like', views.LikeView, name='like'),
    path('liked_posts/<int:id>/', views.liked_posts, name='liked_posts'),
    path('media/<imgfilename>', views.picture, name='picture'),
]