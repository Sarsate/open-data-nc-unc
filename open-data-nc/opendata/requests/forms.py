from django import forms
from selectable.forms import AutoCompleteSelectField
from selectable.forms import AutoCompleteSelectWidget

from opendata.catalog.lookups import CityLookup, CountyLookup
from .models import Request, Bounty, Resource

from django.core.exceptions import ValidationError

import datetime
import re

import types

class SearchForm(forms.Form):
    text = forms.CharField(required=False)


class RequestForm(forms.ModelForm):
    county = AutoCompleteSelectField(
        lookup_class=CountyLookup,
        required=False,
        widget=AutoCompleteSelectWidget(
            lookup_class=CountyLookup,
            attrs={"class": "suggestions-hidden suggestions-county"},
        )
    )
    city = AutoCompleteSelectField(
        lookup_class=CityLookup,
        required=False,
        widget=AutoCompleteSelectWidget(
            lookup_class=CityLookup,
            attrs={"class": "suggestions-hidden suggestions-city"},
        )
    )

    class Meta:
        model = Request
        exclude = ('suggested_by', 'resources', 'rating', 'status', 'supplier')

    class Media:
        js = (
            "suggestions/js/form.js",
        )


class BountyForm(forms.ModelForm):
    class Meta:
        model = Bounty
        exclude = ('request', 'author', 'supplier')

    class Media:
        js = (
            "suggestions/js/form.js",
        )

    def clean(self):
        cleaned_data = super(BountyForm, self).clean()
        due_date = cleaned_data.get("deadline")
        if due_date and due_date < datetime.date.today():
            raise forms.ValidationError('Deadline must be in the future in the format yyyy-mm-dd')
        bounty = cleaned_data.get("price")
        if bounty < 0:
            raise forms.ValidationError('Bounty must be a positive value between 0 and 1000 (ex. 10.50)')
        return cleaned_data


class SupplyForm(forms.ModelForm):
    class Meta:
        model = Resource
        exclude = ('rating', 'proj_coord_sys', 'time_period', 'wkt_geometry', 'csw_typename', 'csw_schema', 'csw_mdsource', 'csw_xml', 'csw_anytext', 'created_by', 'last_updated_by', 'created', 'last_updated', 'metadata_contact', 'metadata_notes', 'coord_sys')

    class Media:
        js = (
            "suggestions/js/form.js",
        )
