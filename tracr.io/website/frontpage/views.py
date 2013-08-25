# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from frontpage.forms import EmailSubscriptionForm
from frontpage.models import EmailSubscription

def index(request):
  if request.method == 'POST':
    form = EmailSubscriptionForm(request.POST)
    if form.is_valid():
      # Save the email address and send an email.
      email_subscription = EmailSubscription(form.email)
      email_subscription.save()

      return HttpResponseRedirect('/thank-you/')
  else:
    form = EmailSubscriptionForm()
    context = RequestContext(request, {'form': form})
    return render_to_response('frontpage/index.html', context)

def thank_you(request):
  context = RequestContext(request, {})
  return render_to_response('frontpage/thank_you.html', context)

