from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
import os
import datetime

class Tag(models.Model): #tagモデルを新しく定義する
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

def dir_path_name(instance, filename):

    file_type = os.path.splitext(filename)  # ファイル名と拡張子を分ける
    date_time = datetime.datetime.now()
    # date_dir = date_time.strftime('%Y/%m/%d')
    time_stamp = date_time.strftime('%H-%M-%S-')
    new_filename = filename

    """ -------追記--------- """
    # １番目の要素である拡張子と同じであれば処理が実行される。
    if file_type[1] == '.png' or file_type[1] == '.jpeg':
        path = os.path.join('media/images', new_filename)
    elif file_type[1] == '.pdf':
        path = os.path.join('media/pdf', new_filename)
    elif file_type[1] == '.py':
        path = os.path.join('media/py', new_filename)
    else:
        path = os.path.join('media/others', new_filename)
    return path


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag) #この行を追加
    image = models.FileField(upload_to=dir_path_name, verbose_name='添付ファイル', null=True, blank=True) # 追加
    # file = models.FileField(upload_to='files', verbose_name='添付ファイル', validatos=[FileExtensionValidator(['pdf', ])], null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def file_name(self):
        if self.image:
            return os.path.basename(self.image.path)

    def file_type(self):
        if self.image:
            _, ext = os.path.splitext(os.path.basename(self.image.path))
            return ext[1:]

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='like')

class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

# ユーザー認証
from django.contrib.auth.models import User

# ユーザーアカウントのモデルクラス
class Account(models.Model):

    # ユーザー認証のインスタンス(1vs1関係)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username