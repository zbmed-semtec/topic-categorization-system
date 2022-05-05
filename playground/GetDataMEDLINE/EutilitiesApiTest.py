from urllib import response
import xml.etree.ElementTree as ET
import requests

r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science[journal]+AND+breast+cancer+AND+2008[pdat]")
xmltxt = r.content
#print(xmltxt)
root = ET.fromstring(xmltxt)

for child in root.iter('*'):
    print(child.tag)

xmlDict = {}
#for sitemap in root:
#    children = sitemap.getchildren()
#    xmlDict[children[0].text] = children[1].text
#print (xmlDict)
