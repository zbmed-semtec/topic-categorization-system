from urllib import response
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import requests

r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=11918830&retmode=xml")
xmltxt = r.content

Bs_data = BeautifulSoup(xmltxt, "xml")
#Bs_data.con
MeshListRaw = Bs_data.find("MeshHeadingList")
MeshList = []
for child in MeshListRaw:
    if child.find("DescriptorName", {'MajorTopicYN':'Y'}) != None:
        MeshList.append(child.contents)

for elem in MeshList:
    print(elem)


#xmlDict = {}
#for sitemap in root:
#    children = sitemap.getchildren()
#    xmlDict[children[0].text] = children[1].text
#print (xmlDict)
