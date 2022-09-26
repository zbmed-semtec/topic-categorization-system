'''
    This class is use to create TSV files with the PMC_id, Title, Abstract, and Mesh terms of articles extracted from the FTP server of  NCBI.
    The Title and Abstract fields are pre processed to delete words and characters that are not useful.
'''

#Reference for the code: https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
from doctest import testfile
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import time

'''
    Function to read the data inside the xml file located in document_path and store it in a BeutifulSoup parser.

    Input:  document_path ->  The path of the input xml file.
    Output: A BeutifulSoup parser
'''

def openXML(document_path):
    with open(document_path, 'r', encoding="mbcs") as f:
        data = f.read()
    
    return BeautifulSoup(data, "xml")

'''
    Function to extract the PubMed and PubMed Central ids from an XML file located in document_path.

    Input:  Bs_data ->  A BeutifulSoup parser with the information of the article.
    Output: A list of two strings containing the PumMed Central id and the Pubmed id of the article.
'''

def getIds(Bs_data):

    # Using find() to extract attributes of the first instance of the tag
    pmc_id = Bs_data.find('infon', {'key':'article-id_pmc'})
    pm_id = Bs_data.find('infon', {'key':'article-id_pmid'})

    if(pmc_id == None):
        pmc_id = 'x'
    
    if(pm_id == None):
        pm_id = 'x'

    return pmc_id.text.strip(),pm_id.text.strip()

'''
    Function to extract the title and abstract of the XML parser.
    The abstract is contained in multiple xml tags, so we need to put it back together.
    Especial words to describe segments of the abstract are remove. 

    Input:  Bs_data ->  A BeutifulSoup parser with the information of the article.
    Output: A list with 2 strings the Title and the abstract of the article.
'''
def getTitleAbstract(Bs_data):
    title = ''
    abstract = []
    for passage in Bs_data.find_all('passage'):
        section_type = passage.find('infon',{"key":"section_type"})
        
        if(section_type.text.strip() == 'ABSTRACT'):
            info = passage.find('text').text.strip()
            keywords_pattern = r"([A-Z]+[A-Z\s&a-z]{2,69}:*)"
            match = re.search(keywords_pattern, info)
            if(match and match.span()[1]-match.span()[0] == len(info)):
                print(match)
            else:
                abstract.append(passage.find('text').text.strip()+" ")
        
        if(section_type.text.strip() == 'TITLE'):
            title = passage.find('text').text.strip()
    
    if(title == ''):
        title = 'x'
    
    if(len(abstract) == 0):
        abstract.append('x')

    return title,''.join(abstract)

'''
    Function to extract the Mesh terms of the XML file.

    Input:  Bs_data ->  A BeutifulSoup parser with the information of the article.
    Output: A list with the Mesh terms.
'''
def getMeshTerms(Bs_data):
    
    Mesh_terms = []
    
    for elem in Bs_data.find('collection').find_all('DescriptorName'):
        Mesh_terms.append(elem.attrs["UI"].strip()+";")

    if(len(Mesh_terms) == 0):
        Mesh_terms.append('x')

    return ''.join(Mesh_terms)    

'''
    Function to retrieve and create a dataset with [PMID, Title, Abstract, MeshTerms] from XML-files.
    
    Input:  inputPath -> Directory with the chunked xml files.
            outputPath -> Directory with the output formatted xml files.
    Output: Returns a tsv file based of a pandas.DataFrame(columns=['PMID', 'title', 'abstract',"MeshTerms"]) 
'''

def process_multiple_xml(directory_origin = "D:\PDG\Datasets\PMC000XXXXX_xml_unicode_small_meshTerms", directory_destiny = "D:\PDG\Datasets\PMC000XXXXX_xml_unicode_small_tsv"):
    df = pd.DataFrame(columns =  ["PMID","Title", "Abstract", "MeshTerms"])
    df_errors = pd.DataFrame(columns =  ["PMID","Title", "Abstract", "MeshTerms"])
    i = 0
    art_id = 0
    art_err_id = 0
    # iterate over files in
    # that directory
    for filename in os.listdir(directory_origin):
        i+=1
        if i == 10:
            break
        f = os.path.join(directory_origin, filename)
        # checking if it is a file
        if os.path.isfile(f):
            BS_article = openXML(f) 
            PMID = getIds(BS_article)
            Title,Abstract = getTitleAbstract(BS_article)
            MeshTerms = getMeshTerms(BS_article)
            if(PMID[1] == 'x' or Title == 'x' or Abstract == 'x' or MeshTerms == 'x'):
                df_errors.loc[art_err_id] = [PMID[1],Title,Abstract,MeshTerms]
                art_err_id+=1
            else:
                df.loc[art_id] = [PMID[1],Title,Abstract,MeshTerms]
                art_id+=1
            
    #print(df)
    #print(df_errors)
    df.to_csv(directory_destiny+"\\Dataset.tsv", sep="\t")
    df.to_csv(directory_destiny+"\\Dataset_errors.tsv", sep="\t")

'''
Test of the execution of the above functions for an individual xml file.
'''
def test_individual_xml():
    test_file = "D:\PDG\Datasets\PMC000XXXXX_xml_unicode_small_meshTerms\PMC100320.xml"
    test_file_destiny = "D:\PDG\Datasets\PMC000XXXXX_xml_unicode_small_tsv\PMC100320.tsv"
    BS_article = openXML(test_file)
    PMID = getIds(BS_article)
    Title,Abstract = getTitleAbstract(BS_article)
    MeshTerms = getMeshTerms(BS_article)
    df = pd.DataFrame(columns =  ["PMID","Title", "Abstract", "MeshTerms"])
    df.loc[0] = [PMID[1],Title,Abstract,MeshTerms]
    print(df.head())
    df.to_csv(test_file_destiny, sep="\t")


#start_time = time.time()
process_multiple_xml()
#print("--- %s seconds ---" % (time.time() - start_time))
