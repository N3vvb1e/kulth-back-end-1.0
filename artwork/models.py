from django.db import models

class Artwork(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} by {self.artist}"
    
    def delete(self, *args, **kwargs):
        self.note_set.all().delete()
        super(Artwork, self).delete(*args, **kwargs)

class Note(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    zone_description = models.TextField()
    title = models.TextField()
    darkness = models.IntegerField(default=0)

    def to_dict(self):
        return {            
            "id": self.id,
            "title": self.title,
            "zone_description": self.zone_description,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }