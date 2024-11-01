from django.forms import ModelForm
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model=Room #specifying the model we are creating the form for 
        fields='__all__'