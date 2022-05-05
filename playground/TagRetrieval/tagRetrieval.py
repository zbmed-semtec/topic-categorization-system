#Reference for the code: https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
from bs4 import BeautifulSoup
import os
import requests
 
def getIds(document_path):
    # Reading the data inside the xml
    # file to a variable under the name
    # data
    with open(document_path, 'r') as f:
        data = f.read()
    
    # Passing the stored data inside
    # the beautifulsoup parser, storing
    # the returned object
    Bs_data = BeautifulSoup(data, "xml")
    
    # Finding all instances of tag
    # `unique`
    #b_unique = Bs_data.find_all('infon')
    
    #print(b_unique)
    
    # Using find() to extract attributes
    # of the first instance of the tag
    pmc_id = Bs_data.find('infon', {'key':'article-id_pmc'})
    pm_id = Bs_data.find('infon', {'key':'article-id_pmid'})
    print("pmc_id",pmc_id.text)
    print("pm_id",pm_id.text)

    return pmc_id.text,pm_id.text
    

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

#ids = getIds("D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small\\PMC100320.xml")

directory = "D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small"
 
i = 0

# iterate over files in
# that directory
for filename in os.listdir(directory):
    i+=1
    if i == 20:
        break
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        MeshList = getMeshTerms(getIds(f))
    
