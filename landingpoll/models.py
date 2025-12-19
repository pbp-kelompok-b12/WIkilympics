from django.db import models

class PollQuestion(models.Model):
    question_text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_votes(self):
        return sum(option.votes for option in self.options.all())

    def __str__(self):
        return self.question_text


class PollOption(models.Model):
    question = models.ForeignKey(PollQuestion, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.option_text
