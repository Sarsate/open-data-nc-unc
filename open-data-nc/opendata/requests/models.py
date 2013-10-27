from django.db import models
from django.contrib.auth.models import User

from djangoratings.fields import RatingField
from opendata.catalog.models import Resource, City, County, Category, \
    UpdateFrequency
from opendata.fields_info import FIELDS, HELP


class Request(models.Model):
    PENDING = 0
    APPROVED = 1
    SUPPLIED = 2

    STATUS = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (SUPPLIED, 'Supplied')
    )
    AGENCY_TYPES = (
        ('state', 'Statewide'),
        ('county', 'County Agency'),
        ('city', 'City/town Agency'),
    )

    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1, choices=STATUS)
    suggested_by = models.ForeignKey(User, related_name="suggested_by")
    title = models.CharField(max_length=255, help_text=HELP['title'])
    description = models.TextField(help_text=HELP['description'])
    relevance = models.TextField(help_text=HELP['relevance'])
    url = models.URLField(verbose_name=FIELDS['url'], blank=True)
    agency_type = models.CharField(verbose_name=FIELDS['agency_type'],
                                  choices=AGENCY_TYPES, max_length=16)
    city = models.ForeignKey(City, related_name='requests', null=True,
                             blank=True)
    county = models.ForeignKey(County, related_name='requests', null=True,
                               blank=True)
    agency_name = models.CharField(max_length=255, blank=True)
    agency_division = models.CharField(max_length=255, blank=True)
    updates = models.ForeignKey(UpdateFrequency, null=True, blank=True,
                                help_text=HELP['update_frequency'],
                                )
    agency_contact = models.CharField(max_length=255, blank=True)
    categories = models.ManyToManyField(Category,
                                        related_name="requests",
                                        null=True, blank=True)
    other_category = models.CharField(u'Other category', max_length=255, blank=True,
                                      help_text=HELP['other'])
    resources = models.ManyToManyField(Resource,
                                       related_name="requests",
                                       null=True, blank=True)
    rating = RatingField(range=1, allow_delete=True, can_change_vote=True)
    supplier = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        permissions = (
            ("can_claim_request", "Can claim request")
        )

    def __unicode__(self):
        return self.title


class Bounty(models.Model):
    request = models.ForeignKey(Request)
    author = models.ForeignKey(User)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    deadline = models.DateField()
