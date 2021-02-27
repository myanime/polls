import uuid

from django.db import models


class PollChoice(models.Model):
    choice = models.CharField(max_length=128)

    def __str__(self):
        return self.choice


class Respondent(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    choices = models.ManyToManyField(PollChoice, blank=True)

    def __str__(self):
        return str(self.uuid)


class Poll(models.Model):
    title = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    question = models.TextField(null=True, blank=True)
    choices = models.ManyToManyField(PollChoice, blank=True)
    respondents = models.ManyToManyField(Respondent, blank=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField(null=True, blank=True)
    respondent = models.ForeignKey(Respondent, null=True, blank=True, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.text}; {self.respondent} - {self.poll}'
