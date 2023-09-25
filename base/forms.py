from django.forms import ModelForm
from . import models
# from .models import Room

class RoomForm(ModelForm):
    
    class Meta:
        model = models.Room
        # fields = "__all__"
        fields = ["topic","name","description"]
        # exclude = ["host","participants"]
