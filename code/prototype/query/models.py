from django.db import models

class MeshTermList(models.Model):
    query_url = models.CharField(max_length=200)
    query_title_abstract = models.CharField(max_length=600)

class MeshTerm(models.Model):
    meshterm_list = models.ForeignKey(MeshTermList, on_delete=models.CASCADE)
    meshterm_text = models.CharField(max_length=200)
