from django.db import models

# Create your models here.
EVENT_TYPES = (
    ('High','High'),
    ('Medium','Medium'),
    ('Low','Low'),
)

SENSOR_TYPES = (
    ('Temperature','Temperature'),
    ('Humidity','Humidity'),
)
class Tower(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length = 200)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return 'T'+str(self.id)+' - '+str(self.name)

class Event(models.Model):
    id=models.AutoField(primary_key=True)
    headline = models.CharField(max_length = 200)
    lat = models.FloatField()
    lng = models.FloatField()
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    detail = models.TextField()
    severity = models.CharField(max_length=30, choices=EVENT_TYPES, default='Low')
    datetime = models.DateTimeField()

    def __str__(self):
        return 'E'+str(self.id)+' - '+self.severity+' - '+str(self.tower.name)

class Sensor(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length = 200)
    lat = models.FloatField()
    lng = models.FloatField()
    device=models.CharField(max_length = 20,default="sensor")
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=30, choices=SENSOR_TYPES, default='Temperature')

    def __str__(self):
        return 'S'+str(self.id)+' - '+self.sensor_type+' - '+str(self.tower.name)

class Camera(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length = 200)
    lat = models.FloatField()
    lng = models.FloatField()
    device=models.CharField(max_length = 20,default="camera")
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="images/")

    def __str__(self):
        return str(self.name)+' - '+str(self.tower.name)

'''
  const locations = [
    {
      name: "Location 1",
      location: { 
        lat: 31.582045,
        lng: 74.329376
      },
    },
    {
      name: "Location 2",
      location: { 
        lat: 31.6,
        lng: 74.3
      },
    },
    {
      name: "Location 3",
      location: { 
        lat: 31.5,
        lng: 74.4
      },
    },
  ];
'''