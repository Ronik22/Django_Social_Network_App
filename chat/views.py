from typing import ContextManager
from django.contrib.auth.models import User
import json
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Chat
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string

# Create your views here.

@login_required
def ChatView(request,id):
    receiver = get_object_or_404(User, id=id)
    sender = request.user
    chats = Chat.objects.filter(
        Q(sender=sender,receiver=receiver) | Q(sender=receiver,receiver=sender)
    ).order_by('date')
    
    if request.method == "POST":
        form = request.POST.get('body')
        newchat = Chat.objects.create(sender=sender, receiver=receiver, text=form)
        newchat.save()

    context = {
        'chats':chats,
        'other_user':receiver,
    }

    if request.is_ajax():
        html = render_to_string('chat/chat_section.html',context, request=request)
        return JsonResponse({'form':html})

    return render(request, 'chat/chat_view.html', context)


# @login_required
# def ajax_load_messages(request,pk):
#     receiver = get_object_or_404(User, id=id)
#     sender = request.user
#     chats = Chat.objects.filter(
#         Q(sender=sender,receiver=receiver) | Q(sender=receiver,receiver=sender)
#     ).order_by('date')
#     # chats.update(has_seen=True)
#     chat_list = [{
#         "sender": chat.sender.username,
#         "chat": chat.text,
#         "sent": chat.sender == sender
#     } for chat in chats ]
#     if request.method == "POST":
#         chat = json.loads(request.body)
#         m = Chat.objects.create(sender=sender, receiver=receiver, text=chat)
#         chat_list.append({
#             "sender": request.user.username,
#             "chat": m.text,
#             "sent": True
#         })
#     return JsonResponse(chat_list, safe=False)


@login_required
def AllChat(request):
    users = User.objects.all()
    context = {
        'users':users
    }
    return render(request, 'chat/all_chats.html', context)
