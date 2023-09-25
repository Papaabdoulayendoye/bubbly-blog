from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth import authenticate, login,logout

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated :
        return redirect('base:home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try :
            user = User.objects.get(Q(username=username))
        except:
            messages.error(request, "User does not exists!")
        user = authenticate(request,username=username,password=password)
        if user :
            login(request,user)
            return redirect("base:home")
        else :
            messages.error(request, "Invalid username or password")
    
    context = {'page' : page}
    return render(request,"base/login_register.html",context)



def logoutUser(request):
    logout(request)
    return redirect("base:login")

def registerPage(request):
    form = UserCreationForm()
    context = {'form' : form}
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('base:home')
        else :
            messages.error(request,"An error occured during registration.")
    
    
    return render(request,"base/login_register.html",context)


def home(request) :
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    roomMessages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    context = {'rooms': rooms,
            'topics': topics, 
            'room_count': room_count,
            'roomMessages' : roomMessages}
    
    return render(request, "base/home.html",context) 

# @login_required
def userProfile(request,pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()
    roomMessages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user, 'roomMessages' : roomMessages ,'rooms' : rooms, 'topics' : topics }
    return render(request,"base/profile.html",context)


def room(request,pk) :
    # getRoom = Room.objects.get(pk=pk)
    getRoom = Room.objects.filter(id=pk).first()
    roomMessages = getRoom.message_set.all().order_by("-created")
    participants = getRoom.participants.all()
    context = {'rooms' : getRoom , 'roomMessages' : roomMessages, 'participants' : participants }
    
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = getRoom,
            body = request.POST.get("body")
        )
        getRoom.participants.add(request.user)
        return redirect('base:room', pk=getRoom.id)
    
    
    return render(request, "base/room.html", context )


@login_required(login_url='base:login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base:home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)


@login_required(login_url='base:login')
def updateRoom(request,pk):
    room = Room.objects.get(pk=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host :
        return HttpResponse("You are not allowed here!!")
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid() :
            form.save()
            return redirect('base:home')
    
    context = {'form':form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='base:login')
def deleteRoom(request,pk) :
    room = Room.objects.get(pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('base:home')
    return render(request,"base/delete.html",{'obj':room})



@login_required(login_url='base:login')
def deleteMessage(request,pk) :
    message = Message.objects.get(pk=pk)
    roomID = message.room.id
    
    
    if request.method == 'POST':
        message.delete()
        return redirect('base:home')
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request,"base/delete.html",{'obj':message})