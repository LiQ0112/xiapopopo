import os

if __name__=="__mian__":
    os.environ.setdefault("DJANGO_SETTING_MODELS","bbs.settings")
    import django
    django.setup()

    from blog import models
    # 查询a1对应的评论数
    ret = models.Article.objects.first().comment_set.all()
    print(ret)

