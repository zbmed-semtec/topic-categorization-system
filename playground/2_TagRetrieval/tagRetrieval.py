'''
    This class is use to extract and insert new tags in the xml files containing the information of articles extracted from the FTP server of  NCBI.
    Tags are used in xml files to give more semantic meaning to their content. 
'''

#Reference for the code: https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
from bs4 import BeautifulSoup
import os
import requests


'''
    Function to read the data inside the xml file located in document_path and store it in a BeutifulSoup parser.

    Input:  document_path ->  The path of the input xml file.
    Output: A BeutifulSoup parser
'''

def openXML(document_path):
    with open(document_path, 'r', encoding="mbcs") as f:
        data = f.read()
    
    return BeautifulSoup(data, "xml")

#

'''
    Function to extract the PubMed and PubMed Central ids from an XML file located in document_path.

    Input:  document_path ->  The path of the input xml file.
    Output: A list of two strings containing the PumMed Central id and the Pubmed id of the article.
'''

def getIds(document_path):
    
    Bs_data = openXML(document_path)
    
    # Using find() to extract attributes of the first instance of the tag
    pmc_id = Bs_data.find('infon', {'key':'article-id_pmc'})
    pm_id = Bs_data.find('infon', {'key':'article-id_pmid'})
    #print("pmc_id",pmc_id.text)
    #print("pm_id",pm_id.text)

    return pmc_id.text,pm_id.text
  

'''
    Function to extract the Mesh terms of an article using an specif PubMed central id, using the ncbi Api. 

    Input:  ids -> A list of two strings containing the PumMed Central id and the Pubmed id of an article.
    Output: MeshList -> A list of strings containing the MeshTerms asociated with the Pubmed central id of the article.
'''

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
    
    return MeshList    

'''
    Function to extract the Mesh terms of an article using an specif PubMed central id, using the ncbi Api. 

    Input:  document_path ->  The path of the input xml file.
            end_path ->  The path where the output xml files will be stored.
    Output: A written xml-file with the new Mesh terms added to it.
'''
def writeMeshTerms(document_path,end_path,MeshList):
    bs_data = openXML(document_path)

    for elem in MeshList:
        #print(elem[0])
        bs_data.find('collection').insert(0,elem[0])
    
    # Output the contents of the
    # modified xml file
    #print(bs_data.prettify())
    #This changes based on the path.
    file_name = document_path.split("\\")[-1]
    #print(file_name)
    f = open(end_path + file_name, "w", encoding="mbcs")
    f.write(bs_data.prettify())
    f.close()

    return 0



'''
Test of the execution of the above functions.
'''
directory_origin = "D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small"
directory_destiny = "D:\\PDG\\Datasets\\PMC000XXXXX_xml_unicode_small_meshterms\\"
i = 0

# iterate over files in
# that directory
for filename in os.listdir(directory_origin):
    f = os.path.join(directory_origin, filename)
    # checking if it is a file
    if os.path.isfile(f):
        MeshList = getMeshTerms(getIds(f))
        if(len(MeshList)>0):
            writeMeshTerms(f,directory_destiny,MeshList)

    
