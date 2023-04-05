from typing import NewType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import Post, Comment, Account, Tag, Like

from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm, PostForm2, MyPasswordChangeForm, TagForm
from django.views.generic import DetailView
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
import os

def post_list(request):
    user = request.user
    posts = Post.objects.filter(published_date__lte=timezone.now())
    tags = Tag.objects.all()
    if request.user.is_authenticated:
        liked_list = [like.post.pk for like in user.like_set.all()]
    keyword = request.GET.get('keyword')
    if keyword:
        posts = posts.filter(
                 Q(title__icontains=keyword) | Q(text__icontains=keyword)
                )
        messages.success(request, '「{}」の検索結果'.format(keyword))
    if request.user.is_authenticated:
        return render(request, 'blog/post_list.html', {'posts': posts, 'tags': tags, 'liked_list': liked_list, 'user': user, })
    return render(request, 'blog/post_list.html', {'posts': posts, 'tags': tags, 'user': user, })

def LikeView(request):
    if request.method =="POST":
        post = get_object_or_404(Post, pk=request.POST.get('post_pk'))
        user = request.user
        liked = False
        like = Like.objects.filter(post=post, user=user)
        if like.exists():
            like.delete()
        else:
            like.create(post=post, user=user)
            liked = True
    
        context={
            'post_pk': post.pk,
            'liked': liked,
            'count': Like.objects.filter(post=post).count(),
        }


    if request.is_ajax():
        return JsonResponse(context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    liked_list = []
    liked = Like.objects.filter(post=post)
    if liked.exists():
        liked_list.append(post.pk)
    # if post.image:
    #     file_type_flag = False
    #     f, file_type = os.path.splitext(os.path.basename(post.image.path))
    #     file_name = os.path.basename(post.image.path)
    #     if file_type == '.jpeg' or file_type == '.png':
    #         file_type_flag = True
    #     return render(request, 'blog/post_detail.html', {'post': post, 'liked_list': liked_list, 'file_name': file_name, 'file_type_flag': file_type_flag})

    return render(request, 'blog/post_detail.html', {'post': post, 'liked_list': liked_list})



@login_required
def tag_create(request):
    if request.method == "POST":
        new_tag = TagForm(request.POST)
        if new_tag.is_valid():
            new_tag_name = new_tag.cleaned_data.get('new_tag')

            if Tag.objects.filter(name=new_tag_name).count():
                return render(request, 'blog/tag_create.html', {'new_tag': new_tag, 'error': 'このタグは既に登録されています'})

            Tag.objects.create(name=new_tag_name)
            return redirect("post_list")

    new_tag = TagForm()
    return render(request, 'blog/tag_create.html', {'new_tag': new_tag})

@login_required
def tag_remove(request,tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    tag.delete()
    return redirect('post_list')

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.image = request.FILES.get('image')
            tags_list = form.cleaned_data.get('tags')
            post.save()

            if tags_list:
                for tag in tags_list:
                    post.tags.add(Tag.objects.get_or_create(name=tag)[0])


            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
            
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form, })

def post_new_2(request):

    if request.method == "POST":
        form = PostForm2(request.POST)
        if form.is_valid():
            post = Post.objects.create(
                author=request.user,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                image=request.FILES.get('image'),
                )

            print(post.tags)    
            tags = form.cleaned_data['tags']
            for tag in tags:
                post.tags.add(tag)

            new_tag = form.cleaned_data['new_tag']

            if new_tag:
                if Tag.objects.filter(name=new_tag).count():
                    return render(request, 'blog/post_edit.html', {'form': form, 'error': 'このタグは既に登録されています'})
                
                new_tag = Tag.objects.create(name=new_tag)
                post.tags.add(new_tag)

            return redirect('post_detail', pk=post.pk)

    else:
        form = PostForm2()
    return render(request, 'blog/post_edit.html', {'form': form,})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)    
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.image = request.FILES.get('image')
            post.save()
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
            
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form,})

@login_required
def post_edit_2(request, pk):
    post = get_object_or_404(Post, pk=pk)
    choices = list(Tag.objects.values_list('pk', 'name'))
    initial_tag = []
    tags = post.tags.all()
    tag_name = set()
    for tag in tags:
        tag_name.add(tag.name)
    for choice in choices:
        choice = list(choice)
        if choice[1] in tag_name:
            initial_tag.append(choice[0])
            
    if request.method == "POST":
        form = PostForm2(request.POST, initial={'title': post.title, 'text': post.text, 'image': post.image, 'tags': initial_tag})

        if form.is_valid():
            post.title = request.POST['title']
            post.author = request.user
            post.text = request.POST['text']
            post.image = request.FILES.get('image')

            post.tags.clear()

            tags = form.cleaned_data['tags']
            #print(post.tags)
            for tag in tags:
                #print(tag)
                post.tags.add(tag)
            
            new_tag = form.cleaned_data['new_tag']

            if new_tag:
                if Tag.objects.filter(name=new_tag).count():
                    return render(request, 'blog/post_edit.html', {'form': form, 'error': 'このタグは既に登録されています'})
                
                new_tag = Tag.objects.create(name=new_tag)
                post.tags.add(new_tag)

            return redirect('post_detail', pk=post.pk)
            
    else:
        form = PostForm2(initial={'title': post.title, 'text': post.text, 'image': post.image, 'tags': initial_tag})
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)

class TagDetail(DetailView): #　追記部分。Detailviewという汎用クラスビューを利用する。
    model = Tag

def post_tag(request, tag_name):
    posts = Post.objects.filter(published_date__lte=timezone.now(), tags__name=tag_name)
    messages.success(request, 'タグ「{}」の投稿一覧'.format(tag_name))
    liked_list = []
    for post in posts:
        liked = Like.objects.filter(post=post)
        if liked.exists():
            liked_list.append(post.pk)
    return render(request, 'blog/post_list.html', {'posts': posts, 'liked_list': liked_list})

@login_required
def liked_posts(request, id):
    user = request.user
    posts = Post.objects.filter(published_date__lte=timezone.now(), like__user=user)
    messages.success(request, '{}さんのいいね一覧'.format(user.username))
    liked_list = []
    for post in posts:
        liked = Like.objects.filter(post=post)
        if liked.exists():
            liked_list.append(post.pk)
    return render(request, 'blog/post_list.html', {'posts': posts, 'liked_list': liked_list})


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'blog/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'blog/password_change_done.html'

from django.views.generic import TemplateView # テンプレートタグ
from .forms import AccountForm # ユーザーアカウントフォーム
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse

class  AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        }

    # Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["AccountCreate"] = False
        return render(request,"blog/register.html",context=self.params)

    # Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)

        # フォーム入力の有効検証
        if self.params["account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新
            account.save()

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        return render(request,"blog/register.html",context=self.params)
    

from django.http import HttpResponse
from mysite import settings

def picture(request, filename):
    file_type = os.path.splitext(filename)  # ファイル名と拡張子を分ける
    if file_type[1] == '.png' or file_type[1] == '.jpeg':
        directory = 'images/'
    elif file_type[1] == '.pdf':
        directory = 'pdf/'
    elif file_type[1] == '.py':
        directory = 'py/'
    else:
        directory = 'others/'
    file_path = os.path.join(settings.IMAGE_ROOT , directory + filename)

    with open(file_path, "rb") as f:  # rbはread binaryのこと
        file = f.read()
    return HttpResponse(file)