from pdb import Restart
import Bio
from Bio import Entrez
import re, nltk
from nltk.stem.snowball import SnowballStemmer
import json
from bs4 import BeautifulSoup

# nltk dependencies
nltk.download('stopwords') #required 
nltk.download('punkt') #required 

# =============================================================================
# Functions for cleaning + pre-processing text data
# =============================================================================
stemmer = SnowballStemmer("english")
stopword_list = nltk.corpus.stopwords.words('english')
stopword_list = stopword_list + ['']

def tokenize_text(txt):
    tokens = nltk.word_tokenize(txt)
    tokens = [token.strip() for token in tokens]
    return tokens


def clean(doc,remove_stopwords=True):
    
    doc=doc.replace('-', ' ')
    
    #remove tags
    doc= re.sub('<[^<]+>', "", doc)
    #tokenize text
    doc_text=tokenize_text(doc)  
    
    doc_text=[x.strip() for x in doc_text]
    
    # keep only text characters
    doc_text= [re.sub("[^a-zA-Z]","", word) for word in doc_text]
    
    # lower text and remove stop words
    words = [word.lower() for word in doc_text]
    if remove_stopwords:
        words = [w for w in words if not w in stopword_list]

    # stem words and re join 
    stems = [stemmer.stem(t) for t in words if t]
    stems = ' '.join(stems)

    return(stems)


def explore1():
    batch_size = 20 
    start = 5000005

    #Get PubMed all pubmed ids from 2015 to today
    Entrez.email = "nelsonquinones2424@gmail.com"
    Entrez.api_key = "abd474bb98c9241472b3642237940f709307"
    handle = Entrez.esearch(db="pubmed",term = "2015/3/1:2022/4/30[Publication Date]",retmode="xml",retstart = start, Retmax = batch_size)
    records = Entrez.read(handle)
    handle.close()


    print(records['Count'])
    print(records['IdList'])
    print(",".join(records['IdList']))
    #handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']), rettype="full" , retmode="xml")
    handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']), rettype="full" , retmode="xml")
    summaries = Entrez.read(handle)
    handle.close()

    

    json_object = json.dumps(summaries, indent = 4) 

    with open("data\\BioEntrez\\BioEntrez_Query_Response.json", "w") as outfile:
        json.dump(summaries, outfile)

    for i in range(batch_size):
        #Title

        try:
            print("Title: ")
            print(summaries["PubmedArticle"][i]["MedlineCitation"]["Article"]["ArticleTitle"])

            #Summary
            print("Summary: ")
            raw_text = "".join(summaries["PubmedArticle"][i]["MedlineCitation"]["Article"]["Abstract"]["AbstractText"])
            clean_text = clean(raw_text)
            print(raw_text)
            print()
            print(clean_text)

            #MeshTerms
            print("Keyword list: ")
            if(len(summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"])>0):
                for key_word in summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"]:
                    print(key_word)
            
            else:
                print("No keyword.")

        except Exception as e:
            print(e)

        print()


#Get the Meshterms of a BeautifulSoup object representing a Pumbmed XML file.

def getMeshTerms(Bs_data):

    MeshListRaw = Bs_data.find("MeshHeadingList")
    MeshList = []
    
    if MeshListRaw != None:
        for child in MeshListRaw:
            if child.find("DescriptorName", {'MajorTopicYN':'Y'}) != None:
                MeshList.append(child.contents[0].attrs["UI"].strip())
    
    return MeshList   


'''
    Function to extract the title of the XML parser.

    Input:  Bs_data ->  A BeautifulSoup parser with the information of the article.
    Output: The Title of the article.
'''
def getTitle(Bs_data):
    title = []
    
    TitleRaw = Bs_data.find("ArticleTitle")
    
    if TitleRaw != None:
        for child in TitleRaw:
            title.append(child.text.strip())
    
    if(len(title) == 0):
        title.append('x')

    return title[0]

'''
    Function to extract the PMID of the XML parser.

    Input:  Bs_data ->  A BeautifulSoup parser with the information of the article.
    Output: The PMID of the article.
'''
def getPMID(Bs_data):
    pmid = []
    
    pmidRaw = Bs_data.find("PMID")
    
    if pmidRaw != None:
        for child in pmidRaw:
            pmid.append(child.text.strip())
    
    if(len(pmid) == 0):
        pmid.append('x')

    return pmid[0]

'''
    Function to extract the abstract of the XML parser.
    The abstract is contained in multiple xml tags, so we need to put it back together.

    Input:  Bs_data ->  A BeautifulSoup parser with the information of the article.
    Output: The raw abstract of the article.
'''
def getAbstract(Bs_data):
    abstract = []
    
    AbstractRaw = Bs_data.find("AbstractText")
    
    if AbstractRaw != None:
        for child in AbstractRaw:
            abstract.append(child.text.strip())
    
    if(len(abstract) == 0):
        return "x"

    return " ".join(abstract)



def explore_getting_Data():
    batch_size = 40 
    start = 5000005

    #Get PubMed all pubmed ids from 2015 to today
    Entrez.email = "nelsonquinones2424@gmail.com"
    Entrez.api_key = "abd474bb98c9241472b3642237940f709307"
    handle = Entrez.esearch(db="pubmed",term = "2015/3/1:2022/4/30[Publication Date]",retmode="xml",retstart = start, Retmax = batch_size)
    records = Entrez.read(handle)
    handle.close()


    print(records['Count'])
    print(records['IdList'])
    print(",".join(records['IdList']))
    #handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']), rettype="full" , retmode="xml")
    handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']) , retmode="xml")
    summaries = handle.read()
    
    
    cnt = 0
    # print(summaries)

    Bs_data = BeautifulSoup(summaries, "xml")

    ArticleList = Bs_data.find("PubmedArticleSet")

    for i  in ArticleList:
        
        Pmid = getPMID(i)
        print(Pmid)
        Title = getTitle(i)
        print(Title)
        Abstract = getAbstract(i)
        print(Abstract)
        MeshListRaw = getMeshTerms(i)
        if(MeshListRaw):
            for j in MeshListRaw:
                print(j)
        
        print("\n")
        # print(i)
        # f = open("data\\BioEntrez\\" + str(cnt)+".xml", "w", encoding="mbcs")
        # f.write(i.prettify())
        # f.close()
        # cnt+=1

    #Bs_data.con
    
    

    # MeshList = getMeshTerms(Bs_data)

    # for i in MeshList:
    #     print(i)

explore_getting_Data()