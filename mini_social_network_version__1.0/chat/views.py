from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from django.contrib.humanize.templatetags.humanize import naturaltime

from django.contrib.auth.models import User
from django.contrib import messages

from chat.models import Message


@login_required
def talk_main(request, slug):
    if request.method == 'POST':
        r = get_object_or_404(User, username=slug).profile
        message = Message(text=request.POST['message'], owner=request.user.profile, recipient=r)
        message.save()

        messages.add_message(request, messages.SUCCESS, 'message send.')

        return redirect(reverse('nsusers:profile', args=[slug]))

    ctx = {'slug': slug}
    return render(request, 'chat/talk.html', ctx)

@login_required
def talk_message(request):
    messages = Message.objects.filter(recipient=request.user.profile).order_by('-created_at')[:16]
    results = []
    for message in messages:
        result = [message.text, naturaltime(message.created_at), message.owner.user.username, message.id, message.is_read]
        results.append(result)
    return JsonResponse(results, safe=False)


@login_required
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    readCount = messageRequests.filter(is_read=True).count()
    context = {'readCount': readCount, 'unreadCount': unreadCount}
    return render(request, 'chat/inbox.html', context)


@login_required
def viewMessage(request):
    query = request.GET
    message = None
    if query:
        message = get_object_or_404(Message, id=query['q'], recipient=request.user.profile)
        if message.is_read == False:
            message.is_read = True
            message.save()
    context = {'message': message}
    return render(request, 'chat/message.html', context)