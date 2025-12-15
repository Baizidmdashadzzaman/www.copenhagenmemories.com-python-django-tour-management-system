from django.shortcuts import redirect, render
from .models import Todo

# Create your views here.

def todo_list(request):
        todos = Todo.objects.all()
        context = { 'todos': todos }
        return render(request, 'todo/index.html', context)


def creaate_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Todo.objects.create(title=title, description=description)
    
    return redirect('todo_list')


def toggle_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')

def delete_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id)
    todo.delete()
    return redirect('todo_list')

def edit_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id)
    if request.method == 'POST':
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        todo.save()
        return redirect('todo_list')
    
    context = { 'todo': todo }
    return render(request, 'todo/edit.html', context)
