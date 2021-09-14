from django.views import View

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.humanize.templatetags.humanize import naturaltime

from django.contrib.auth.models import User
from django.contrib import messages

from chat.models import Message


class TalkMain(LoginRequiredMixin, View):
    template_name = 'chat/talk.html'
    success_url = reverse_lazy('nschat:inbox')
    
    def get(self, request, slug):
        ctx = {'slug': slug}
        return render(request, self.template_name, ctx)

    def post(self, request, slug) :
        r = get_object_or_404(User, username=slug).profile
        message = Message(text=request.POST['message'], owner=request.user.profile, recipient=r)
        message.save()

        messages.add_message(request, messages.SUCCESS, 'message send.')

        return redirect(self.success_url)


class TalkMessages(LoginRequiredMixin, View):
    def get(self, request):
        messages = Message.objects.filter(recipient=request.user.profile).order_by('-created_at')
        results = []
        for message in messages:
            result = [message.text, naturaltime(message.created_at), message.owner.user.username, message.id, message.is_read]
            results.append(result)
        return JsonResponse(results, safe=False)


class Inbox(LoginRequiredMixin, View):
    template_name = 'chat/inbox.html'

    def get(self, request):
        profile = request.user.profile
        messageRequests = profile.messages.all()
        unreadCount = messageRequests.filter(is_read=False).count()
        readCount = messageRequests.filter(is_read=True).count()
        context = {'readCount': readCount, 'unreadCount': unreadCount}
        return render(request, self.template_name, context)


class ViewMessage(LoginRequiredMixin, View):
    template_name = 'chat/message.html'

    def get(self, request):
        query = request.GET
        message = None
        if query:
            message = get_object_or_404(Message, id=query['q'], recipient=request.user.profile)
            if message.is_read == False:
                message.is_read = True
                message.save()
        context = {'message': message}
        return render(request, self.template_name, context)