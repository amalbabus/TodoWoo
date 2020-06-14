from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from todo.forms import FormTodo
from todo.models import Todo
from django.utils import timezone
# Create your views here.
def index(request):
    return(render(request,'todo/index.html'))


def signupuser(request):
    if(request.method=='GET'):
        return(render(request,'todo/signupuser.html',{'form':UserCreationForm()}))
    else:
        if(request.POST['password1']==request.POST['password2']):
            try:
                
                user=User.objects.create_user(username= request.POST['username'] ,password=request.POST['password1'])
                user.save()
                login(request,user)
                return(redirect('currenttodos'))
            except IntegrityError:
                return(render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':'Username already taken'}))

        else:
            return(render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':'password didnt match'}))
@login_required 
def logoutuser(request):

    logout(request)
    return(redirect('index'))


def loginuser(request):
    if(request.method=='GET'):
        return(render(request,'todo/loginuser.html',{'form':AuthenticationForm()}))
    else:
        user = authenticate(password=request.POST['password'] , username=request.POST['username'] )

        if (user is None):
            return(render(request,'todo/loginuser.html',{'form':AuthenticationForm(),'error': 'no user found' }))
        else:
            login(request,user)
            return(redirect('currenttodos'))



@login_required 
def currenttodos(request):
    todos = Todo.objects.filter(user= request.user, datecompleted__isnull=True)
    count =Todo.objects.filter(user= request.user, datecompleted__isnull=True).count()
    if(count==0):
        return(render(request,'todo/current.html',{'message': 'Your Todo is empty. Click Create to add one'}))
    else:
        return(render(request,'todo/current.html',{'todos': todos}))
@login_required 
def createtodo(request):
    if(request.method=='GET'):
        return(render(request,'todo/createtodo.html',{'form': FormTodo()}))
    else:
        try:
            form= FormTodo(request.POST)
            newtodo= form.save(commit=False)
            newtodo.user= request.user
            newtodo.save()
            return(redirect('currenttodos'))
        except ValueError:
            return(render(request,'todo/createtodo.html',{'form': FormTodo(),'error':'some error with input'}))
        
@login_required 
def viewtodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk, user= request.user)
    if(request.method=='GET'):
        form = FormTodo(instance=todo)
        return(render(request,'todo/viewtodo.html',{'form': form,'todo':todo,}))
    else:
        try:
            form = FormTodo(request.POST,instance=todo)
            
            form.save()
            return(redirect('currenttodos'))
        except ValueError:
            return(render(request,'todo/viewtodo.html',{'todo':todo,'form': form,'error':'enter correct way'}))

@login_required 
def completetodo(request, todo_pk):
    if(request.method=='POST'):
        todo=get_object_or_404(Todo,pk=todo_pk, user= request.user)
        todo.datecompleted= timezone.now()
        todo.save()
        return(redirect('currenttodos'))

@login_required 
def completedtodo(request):
    todos = Todo.objects.filter(user= request.user, datecompleted__isnull=False)

    return(render(request,'todo/completedtodo.html',{'todos': todos}))

@login_required 
def deletetodo(request, todo_pk):
    if(request.method=='POST'):
        todo=get_object_or_404(Todo,pk=todo_pk, user= request.user)
        todo.delete()
        return(redirect('currenttodos'))
