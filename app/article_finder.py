from distutils.log import error
from pdb import Restart
import Bio
from Bio import Entrez
import re
import nltk
from nltk.stem.snowball import SnowballStemmer
import time
from threading import Thread
from bs4 import BeautifulSoup

def getXMLData(Bs_data, feature):
    data = []

    DataRaw = Bs_data.find(feature)

    if DataRaw != None:
        for child in DataRaw:
            data.append(child.text.strip())

    if(len(data) == 0):
        return "x"

    return " ".join(data)


def process_article(articleInfo_xml):
    id = "_"
    error_code = ['.', '.', '.', '.']
    try:
        id = getXMLData(articleInfo_xml, "PMID")
        raw_title = getXMLData(articleInfo_xml, "ArticleTitle")
        raw_abstract = getXMLData(articleInfo_xml, "AbstractText")

        article = {}
        article['title'] = raw_title
        article['abstract'] = raw_abstract

        return article

    except Exception as e:
        print(e)         

Entrez.email = "nelsonquinones2424@gmail.com"
Entrez.api_key = "abd474bb98c9241472b3642237940f709307"

def getArticlesData(id_List):
    can = False
    Bs_data = None
    while can == False:
        try:
            can = True
            handle = Entrez.efetch(
                db="pubmed", id=",".join(id_List), retmode="xml")
            articles_List_raw = handle.read()

            Bs_data = BeautifulSoup(articles_List_raw, "xml")
        except Exception as e:
            time.sleep(0.5)
            can = False
            print(e)

    return Bs_data.find("PubmedArticleSet")

def getArticleData(id):
  artdata = getArticlesData([str(id)])
  for i  in artdata:
    return process_article(i)
  