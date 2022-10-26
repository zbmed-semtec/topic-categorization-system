from django import forms

class QueryURLForm(forms.Form):
    url = forms.CharField(label="Pubmed URL", max_length=200)
class QueryTitleAbstractForm(forms.Form):
    title_abstract = forms.CharField(label="Title/Abstract", max_length=600)