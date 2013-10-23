from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from djangoratings.exceptions import CannotDeleteVote

from .models import *
from .forms import SearchForm, RequestForm, BountyForm


def list_requests(request):
    """List current requests"""
    requests = Request.objects.filter(status=Request.APPROVED).order_by("-rating_score")
    bounties = Bounty.objects.filter()
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['text']
            requests = requests.filter(title__icontains=query)
    else:
        form = SearchForm()
    context = {
        'form': form,
        'requests': requests,
        'bounties': bounties,
    }
    return render(request, 'requests/list.html', context)


@login_required
def add_request(request):
    """Add new requests"""
    if request.method == 'POST':
        requestForm = RequestForm(request.POST)
        bountyForm = BountyForm(request.POST)
        if requestForm.is_valid() and bountyForm.is_valid():

            request_object = requestForm.save(commit=False)
            request_object.suggested_by = request.user
            request_object.save()

            bounty_object = bountyForm.save(commit=False)
            bounty_object.author = request.user
            bounty_object.request = request_object
            bounty_object.supplier = request.user
            bounty_object.save()

            request_object.rating.add(score=1, user=request.user,
                                ip_address=request.META['REMOTE_ADDR'])
            return redirect(reverse('request-list'))
    else:
        requestForm = RequestForm()
        bountyForm = BountyForm()
    context = {
        'requestForm': requestForm,
        'bountyForm': bountyForm
    }
    return render(request, 'requests/create_edit.html', context)


@login_required
def add_bounty(request, request_id):
    """Add new bounties"""
    if request.method == 'POST':
        form = BountyForm(request.POST)
        if form.is_valid():
            request_object = get_object_or_404(Request, pk=request_id)
            bounty_object = form.save(commit=False)
            bounty_object.author = request.user
            bounty_object.request = request_object
            bounty_object.supplier = request.user  # Temporary value, TO BE FIXED
            bounty_object.save()
            return redirect(reverse('request-list'))
    else:
        form = BountyForm()
    context = {
            'form': form
    }
    return render(request, 'requests/create_bounty.html', context)


@login_required
@require_POST
def vote(request, request_id):
    """Vote for a requests"""
    request_object = get_object_or_404(Request, pk=request_id)
    voted = request_object.rating.get_rating_for_user(request.user,
                                              request.META['REMOTE_ADDR'])
    if not voted:
        request_object.rating.add(score=1, user=request.user,
                           ip_address=request.META['REMOTE_ADDR'])
    return redirect(reverse('request-list'))


@login_required
@require_POST
def remove_vote(request, request_id):
    """Remove pre-existing vote for requests"""
    request_object = get_object_or_404(Request, pk=request_id)
    try:
        request_object.rating.delete(request.user, request.META['REMOTE_ADDR'])
    except CannotDeleteVote:
        # vote didn't exist, just move on
        pass
    return redirect(reverse('request-list'))

@login_required
@require_POST
def claim_request(request, request_id):
    """Claim request for current user"""
    request_object = get_object_or_404(Request, pk=request_id)
    if not request_object.supplier:
        request_object.supplier = request.user
        request_object.save()
    return redirect(reverse('request-list'))

@login_required
@require_POST
def supply_request(request, request_id):
   """Supply information for current request"""
   request_object = get_object_or_404(Request, pk=request_id)
   return redirect(reverse('request-list'))
