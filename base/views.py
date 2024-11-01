from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout 
from .models import Room,Topic,Message
from .forms import RoomForm
from django.db.models import Q #fro dynamic searching
# Create your views here.

# rooms=[
#     {'id':1, 'name':'Learn Python'},
#     {'id':2, 'name':'Learn dESIGN'},
#     {'id':3, 'name':'Learn Vue'},
# ]

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username OR password is invalid')  

    context={'page':page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    form=UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False) # gives abolity to clean data after user has entered
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request,'An error occurred during registration')

    return render(request, 'base/login_register.html',{'form':form})


def home(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        # Q(host__icontains=q)
         ) #got topic from parent model #icontains makes parameters case sensitive so '' means everything included
    topics=Topic.objects.all()
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms': rooms, 'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html',context)

def room(request,pk):
    # room=None
    # for i in rooms:
    #     if i['id']==int(pk):
    #         room=i
    room=Room.objects.get(id=pk)
    participants=room.participants.all() #.all() for many f=to relation , _set.all() for one to many
    room_messages=room.message_set.all().order_by('-created') #filterung most recent messages based on time created
    if request.method == "POST":
        message= Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html',context)   

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)


@login_required(login_url='login') #redirecting to login page if not logged in before creating a room
def createRoom(request):
    form=RoomForm()
    if request.method =='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room =Room.objects.get(id=pk)
    form=RoomForm(instance=room)

    if request.user!=room.host:
        return HttpResponse('You are not allowed here')
    if request.method=='POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user!=room.host:
        return HttpResponse('You are not allowed here')
    if request.method =='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user!=message.user:
        return HttpResponse('You are not allowed here')
    if request.method =='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})