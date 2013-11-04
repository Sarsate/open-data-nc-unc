from django.conf.urls import patterns, url
from opendata.requests import views


urlpatterns = patterns('',
   url(r'^$', views.list_requests, name="request-list"),
   url(r'^create/$', views.add_request, name="request-create"),
   url(r'^(?P<request_id>\d+)/bounty/$', views.add_bounty, name="bounty-create"),
   url(r'^(?P<request_id>\d+)/vote/$', views.vote,
       name="request-vote"),
   url(r'^(?P<request_id>\d+)/unvote/$', views.remove_vote,
       name="request-remove-vote"),
   url(r'^(?P<request_id>\d+)/claim/$', views.claim_request, name="claim-request"),
   url(r'^(?P<request_id>\d+)/supply/$', views.supply_request, name="supply-request"),
)
