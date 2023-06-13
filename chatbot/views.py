from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from .config import api_key

from django.utils import timezone

openai.api_key = api_key

def ask_openai(message):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = message,
        max_tokens = 150,
        n = 1,
        stop = None,
        temperature = 0.7,
    )
    # print(response)

    answer = response.choices[0].text.strip()
    return answer

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST': ## jeśli metoda dla requestu to POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None: ## jeśli user nie jest nieznany (czyli istnieje w naszej bazie danych):
            auth.login(request, user)
            return redirect('chatbot') ## 'chatbot' -> chatbot/urls.py path(name='chatbot')
        else: ## jeśli user nie istnieje w bazie danych
           error_message = 'Invalid login data'
           return render(request, 'login.html', {'error_message': error_message}) 
    else: ## jeśli metodą dla requestu NIE jest POST:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username'] ## 'username' = <input name='username'> in register.html
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})

        else:
            error_message = "Password don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login') ## 'login' -> chatbot/urls.py path(name='login')