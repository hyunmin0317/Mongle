from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)                      # 데이터명 - 0
    category = models.CharField(max_length=500, blank=True)         # 카테고리 - 1
    agency = models.CharField(max_length=500, blank=True)           # 기관 - 2
    update_date = models.CharField(max_length=500, blank=True)      # 업데이트 주기 - 4
    content = models.TextField()                                    # 설명 - 10
    url = models.CharField(max_length=500, blank=True)              # 데이터 url - 14

    create_date = models.DateTimeField()                            # 등록일
    modify_date = models.DateTimeField(null=True, blank=True)       # 수정일


    voter = models.ManyToManyField(User, related_name='voter_question')

    def __str__(self):
        return self.subject

class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')

    def __str__(self):
        return self.content

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content