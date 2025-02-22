from django.db import models

class Poll(models.Model):
    message_id = models.CharField(max_length=32)

    
class VoteOption(models.Model):
    text = models.CharField(max_length=128)
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE
    )


class UserVoteItem(models.Model):
    user_id = models.CharField(max_length=128)
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
    )
    option = models.ForeignKey(
        to=VoteOption,
        on_delete=models.CASCADE,
        null=True
    )

