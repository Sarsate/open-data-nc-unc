from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from djangoratings.exceptions import CannotDeleteVote
from datetime import date
from django.conf import settings
from django.views.generic import DetailView

from .models import *
from .forms import SearchForm, RequestForm, BountyForm, SupplyForm


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
    requestID_bounty = {}
    for r in requests:
        bountyTotal = 0
        for bounty in bounties:
            if bounty.request == r and bounty.deadline >= date.today():
                bountyTotal += bounty.price
        requestID_bounty[r.title] = bountyTotal
    context = {
        'form': form,
        'requests': requests,
        'bounties': bounties,
        'requestID_bounty': requestID_bounty,
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
@require_POST
def drop_request(request, request_id):
    request_object = get_object_or_404(Request, pk=request_id)
    request_object.status = Request.REMOVED
    request_object.save() 
    return redirect(reverse('request-list'))


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
def claim_request(request, request_id):
    """Claim request for current user"""
    request_object = get_object_or_404(Request, pk=request_id)
    if not request_object.supplier:
        request_object.supplier = request.user
        request_object.save()
    return redirect(reverse('request-list'))


@login_required
@require_POST
def drop_claim(request, request_id):
    """Drop a valid claim on request"""
    request_object = get_object_or_404(Request, pk=request_id)
    if request.user == request_object.supplier:
        request_object.supplier = None
        request_object.save()
    return redirect(reverse('request-list'))


@login_required
@require_POST
def supply_request(request, request_id):
    """Supply information for current request"""
    if request.method == 'POST':
        request_object = get_object_or_404(Request, pk=request_id)
        bounties = request_object.bounty_set.all()
        totalBounty = 0
        for bounty in bounties:
            if bounty.deadline >= date.today():
                totalBounty += bounty.price

        form = SupplyForm(request.POST)
        if form.is_valid():
            resource_object = form.save(commit=False)
            resource_object.created_by = request.user
            resource_object.last_updated_by = request.user
            resource_object.created = date.today()
            resource_object.last_updated = date.today()
            resource_object.save()
            request_object.status = 2
            request_object.save()
            return redirect(reverse('request-list'))
    else:
        form = SupplyForm()
    context = {
            'form': form,
            'totalBounty' : totalBounty
    }
    return render(request, 'requests/supply_request.html', context)

@login_required
@require_POST
def drop_bounty(request, bounty_id):
    """Remove the bounty, dog"""
    if request.method == 'POST':
        bounty_object = get_object_or_404(Bounty, pk=bounty_id)
        bounty_object.delete()

    return redirect(reverse('request-detail', args=(bounty_object.request.id,)))

@login_required
@require_POST
def edit_bounty(request, bounty_id):
    """Edit the bounties, dog"""
    if request.method == 'POST':
        bounty_object = get_object_or_404(Bounty, pk=bounty_id)
        form = BountyForm(request.POST)
        if form.is_valid():
            bounty_object.price = form.cleaned_data['price']
            bounty_object.deadline = form.cleaned_data['deadline']
            bounty_object.save()
            return redirect(reverse('request-list'))
        else :
            if not ('deadline' in request.POST or 'price' in request.POST): 
                bounty_object = Bounty.objects.filter(id=bounty_id)
                data_dict = {'price': bounty_object[0].price, 'deadline': bounty_object[0].deadline}
                form = BountyForm(data_dict)
            
    else:
            form = BountyForm()
    context = { 
        'bounty': bounty_object,
        'form' : form,
    }
    return render(request, 'requests/edit_bounty.html', context)

class RequestDetail(DetailView):
    model = Request
    def get_context_data(self, **kwargs):
        context = super(RequestDetail, self).get_context_data(**kwargs)
        bounties = Bounty.objects.filter()
        context['resource'] = context['object']
        context['bounties'] = bounties
        return context



