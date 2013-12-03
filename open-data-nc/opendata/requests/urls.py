from django.conf.urls import patterns, url
from opendata.requests import views


urlpatterns = patterns('',
   url(r'^$', views.list_requests, name="request-list"),
   url(r'^create/$', views.add_request, name="request-create"),
   url(r'^(?P<request_id>\d+)/dropRequest/$', views.drop_request, name="drop-request"),
   url(r'^(?P<request_id>\d+)/bounty/$', views.add_bounty, name="bounty-create"),
   url(r'^(?P<request_id>\d+)/vote/$', views.vote,
       name="request-vote"),
   url(r'^(?P<request_id>\d+)/unvote/$', views.remove_vote,
       name="request-remove-vote"),
   url(r'^(?P<request_id>\d+)/claim/$', views.claim_request, name="claim-request"),
   url(r'^(?P<request_id>\d+)/drop_claim/$', views.drop_claim, name="drop-claim"),
   url(r'^(?P<request_id>\d+)/supply/$', views.supply_request, name="supply-request"),
   url(r'^(?P<pk>\d+)/$', views.RequestDetail.as_view()),
   url(r'^(?P<bounty_id>\d+)/edit/$', views.edit_bounty, name="edit-bounty"),
)
