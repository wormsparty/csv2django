from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    age = models.IntegerField()
    joined_at = models.DateField()
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

