#Reference for the code: https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
from bs4 import BeautifulSoup
import os
import requests

 # Reading the data inside the xml file located in document_path
 # and store it in the beutifulsoup parser 
def openXML(document_path):
    with open(document_path, 'r') as f:
        data = f.read()

    # Passing the stored data inside
    # the beautifulsoup parser, storing
    # the returned object
    return BeautifulSoup(data, "xml")

# Extract the PumMed and PumMed Central ids from an XML file
# located in document_path
def getIds(document_path):
    
    Bs_data = openXML(document_path)
    
    # Using find() to extract attributes
    # of the first instance of the tag
    pmc_id = Bs_data.find('infon', {'key':'article-id_pmc'})
    pm_id = Bs_data.find('infon', {'key':'article-id_pmid'})
    print("pmc_id",pmc_id.text)
    print("pm_id",pm_id.text)

    return pmc_id.text,pm_id.text
  
# Extract the Mesh terms of an article 
# Using an specif PubMed central id 
def getMeshTerms(ids):
    pmc_id = ids[0]
    pm_id = ids[1]
    r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="+pm_id+"&retmode=xml")
    xmltxt = r.content

    Bs_data = BeautifulSoup(xmltxt, "xml")
    #Bs_data.con
    MeshListRaw = Bs_data.find("MeshHeadingList")
    MeshList = []
    
    if MeshListRaw != None:
        for child in MeshListRaw:
            if child.find("DescriptorName", {'MajorTopicYN':'Y'}) != None:
                MeshList.append(child.contents)

        for elem in MeshList:
            print(elem)
    
    return MeshList    

def writeMeshTerms(document_path,end_path,MeshList):

    bs_data = openXML(document_path)

    for elem in MeshList:
        print(elem[0])
        bs_data.find('collection').insert(0,elem[0])
    
    # Output the contents of the
    # modified xml file
    print(bs_data.prettify())
    file_name = document_path.split("\\")[4]
    print(file_name)
    f = open(end_path + file_name, "w")
    f.write(bs_data.prettify())
    f.close()

    return 0

#ids = getIds("D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small\\PMC100320.xml")

directory_base = "D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small"
 
directory_destiny = "D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small_meshterms\\"

i = 0

# iterate over files in
# that directory
for filename in os.listdir(directory_base):
    i+=1
    if i == 2:
        break
    f = os.path.join(directory_base, filename)
    # checking if it is a file
    if os.path.isfile(f):
        MeshList = getMeshTerms(getIds(f))
        writeMeshTerms(f,directory_destiny,MeshList)
    
