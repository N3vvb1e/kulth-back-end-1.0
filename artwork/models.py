from django.db import models

class Artwork(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Note(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    zone_description = models.TextField()

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "text": self.zone_description,
        }