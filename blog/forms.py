from django import forms
from .models import Post, Comment, Tag, Like
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm

class TagForm(forms.Form):
    new_tag = forms.CharField(label='new tag', max_length=200)

class PostForm(forms.ModelForm):
    tags = forms.CharField(label='tags', required=False)
    
    class Meta:
        model = Post
        fields = ('title', 'text', 'image',)

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        tags_list = tags.split(",")
        return tags_list

class PostForm2(forms.Form):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    image = forms.FileField(required=False)
    tags = forms.MultipleChoiceField(choices=Tag.objects.values_list('pk', 'name'), required=False)
    new_tag = forms.CharField(label='new tag', max_length=200, required=False)

    #(('1', '犬'),('2', '猫'),('3', 'うさぎ'))

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)


class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


from django.contrib.auth.models import User
from .models import Account

# フォームクラス作成
class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    class Meta():
        # ユーザー認証
        model = User
        # フィールド指定
        fields = ('username','email','password')
        # フィールド名指定
        labels = {'username':"ユーザーID",'email':"メール"}