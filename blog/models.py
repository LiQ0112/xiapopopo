from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
'''
用户信息表
'''
class UserInfo(AbstractUser):
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11,null=True,unique=True)
    avatar = models.FileField(upload_to='avatars/')
    create_time = models.DateTimeField(auto_now=True,null=True)
    blog = models.OneToOneField(to='Blog',to_field='nid',null='True')

    def __str__(self):
        return self.username
    class Meta():
        verbose_name = "用户信息"

'''
博客表
'''
class Blog(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)#个人博客标题
    site = models.CharField(max_length=16,unique=True)#个人博客后缀
    theme = models.CharField(max_length=16,null=True)#个人博客主题

    def __str__(self):
        return self.title

    class Meta():
        verbose_name = "博客信息"

'''个人博客文章分类表'''
class Category(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16)
    blog = models.ForeignKey(to='Blog',to_field='nid')

    def __str__(self):
        return self.title
    class Meta():
        verbose_name = "分类"
'''标签表'''
class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    blog = models.ForeignKey(to='Blog',to_field='nid')

    def __str__(self):
        return self.title

    class Meta():
        verbose_name = "标签"

'''文章表'''
class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    desc = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    category = models.ForeignKey(to='Category',to_field='nid',null=True)
    user = models.ForeignKey(to='UserInfo',to_field='nid')
    # 评论数
    comment_count = models.IntegerField(verbose_name="评论数",default=0)
    # 点赞数
    up_count = models.IntegerField(verbose_name="点赞数",default=0)
    # 踩
    down_count = models.IntegerField(verbose_name="点踩数",default=0)
    tags = models.ManyToManyField(
        to='Tag',
        through='ArticleToTag',
        through_fields=('article','tag')
    )

    def __str__(self):
        return self.title

    class Meta():
        verbose_name = "文章"


'''文章详情表'''
class ArticleDetail(models.Model):
    nid = models.AutoField(primary_key=True)
    content = models.TextField()
    article = models.OneToOneField(to='Article',to_field='nid')

    class Meta():
        verbose_name = "文章详情"

'''文章和标签多对多的关系表'''

class ArticleToTag(models.Model):
    nid = models.AutoField(primary_key=True)
    tag = models.ForeignKey(to='Tag',to_field='nid')
    article = models.ForeignKey(to='Article',to_field='nid')

    def __str__(self):
        return "{}--{}".format(self.article.title,self.tag.title)

    class Meta():
        unique_together = (("article","tag"),)


'''点赞表'''
class ArticleUpDown(models.Model):
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo',to_field='nid')
    article = models.ForeignKey(to='Article',to_field='nid')
    is_up = models.BooleanField(default=True)

    class Meta():
        unique_together = (('article','user'),)
        verbose_name = "点赞表"

'''评论表'''
class Comment(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article',to_field='nid')
    user = models.ForeignKey(to='UserInfo',to_field='nid')
    content = models.TextField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey("self",null=True,blank=True)

    def __str__(self):
        return self.content
