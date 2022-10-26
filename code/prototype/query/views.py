from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import redirect
from bs4 import BeautifulSoup
import requests
import pandas as pd

from .forms import QueryURLForm, QueryTitleAbstractForm
from .models import MeshTerm, MeshTermList

filename = "C://Users//sleep//Desktop//PDG//topic-categorization-system//data//phase3//final_dataset.tsv"

def index(request):
    if request.method == 'POST':
        formurl = QueryURLForm(request.POST)
        formtitleabstract = QueryTitleAbstractForm(request.POST)
        if formurl.is_valid():
            try:
                r = requests.get(formurl.cleaned_data["url"])
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                raise SystemExit(e)
            
            xmltxt = r.content
            bs_data = BeautifulSoup(xmltxt, "xml")
            meshListRaw = bs_data.find("MeshHeadingList")
            meshterm_list = MeshTermList(query_url=formurl.cleaned_data["url"])
            meshterm_list.save()
            for child in meshListRaw:
                if child.find("DescriptorName", {'MajorTopicYN':'Y'}) != None:
                    meshterm = MeshTerm(meshterm_text=child.find("DescriptorName").contents, meshterm_list=meshterm_list)
                    meshterm.save()

            return redirect('./results/%d' % meshterm_list.pk)
        if formtitleabstract.is_valid():
            form_title_abstract = formtitleabstract.cleaned_data["title_abstract"]
            df = pd.read_csv(filename,sep='\t')
            df.reset_index(drop=True, inplace=True)
            meshterm_list = MeshTermList(query_title_abstract=form_title_abstract)
            meshterm_list.save()
            for ind in df.index:
                if df['Title/Abstract'][ind] == form_title_abstract:
                    mesh_list = df['MeshTerms'][ind].split(';')
                    for mesh in mesh_list:
                        meshterm = MeshTerm(meshterm_text=mesh, meshterm_list=meshterm_list)
                        meshterm.save()
            return redirect('./results/%d' % meshterm_list.pk)
    else:  # The form is invalid 
        formurl = QueryURLForm()
        formtitleabstract = QueryTitleAbstractForm()
    return render(request, 'index.html', {'formurl': formurl, 'formtitleabstract': formtitleabstract})

def results(request, meshlist_id):
    meshterm_list = MeshTerm.objects.filter(meshterm_list=meshlist_id)
    context = {
        'meshterm_list': meshterm_list,
    }
    return render(request, 'results.html', context)
        