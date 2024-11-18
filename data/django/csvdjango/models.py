from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    age = models.IntegerField()
    joined_at = models.DateField()
    parent = models.ForeignKey('User', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.id)

class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=255)

    def __str__(self):
        return str(self.id)

