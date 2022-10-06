from distutils.log import error
from numpy import record
import pandas as pd
from pdb import Restart
import Bio
from Bio import Entrez
import re, nltk
from nltk.stem.snowball import SnowballStemmer
import time
from threading import Thread
from bs4 import BeautifulSoup

# =============================================================================
# Functions for cleaning + pre-processing text data
# =============================================================================

# nltk dependencies
nltk.download('stopwords') #required 
nltk.download('punkt') #required

stemmer = SnowballStemmer("english")
stopword_list = nltk.corpus.stopwords.words('english')
stopword_list = stopword_list + ['']


'''
    Function to split a string based on spaces, to process individual words.

    Input:  txt ->  The string to tokenize.
    Output: A list of tokens without spaces.
'''

def tokenize_text(txt):
    tokens = nltk.word_tokenize(txt)
    tokens = [token.strip() for token in tokens]
    return tokens

'''
    Function to clean text, which implies tokenizing, lowercasing, stemming and the removal of stop words and tags.

    Input:  doc ->  The text that needs to be cleaned.
            remove_stopwords -> A boolean variable to control the removal of stop words.
    Output: A string
'''
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


# =============================================================================
# Functions to create the Dataset
# =============================================================================


'''
    Function to extract a feature of the XML parser.
    The information is contained in multiple xml tags, so we need to put it back together.

    Input:  Bs_data ->  A BeautifulSoup parser with the information of the article.
            feature ->  A String with the name of the tag we want to get the information.

    Output: The feature of the article as a String. If no feature is found an x is returned.
'''
def getXMLData(Bs_data,feature):
    data = []
    
    DataRaw = Bs_data.find(feature)
    
    if DataRaw != None:
        for child in DataRaw:
            data.append(child.text.strip())
    
    if(len(data) == 0):
        return "x"

    return " ".join(data)

'''
    Function to extract the Mesh terms of the XML parser.

    Input:  Bs_data ->  A BeautifulSoup parser with the information of the article.
    Output: A list with the Mesh terms. If no Mesh term is found an x is returned.
'''
def getMeshTerms(Bs_data):
    
    MeshListRaw = Bs_data.find("MeshHeadingList")
    MeshList = []
    
    if MeshListRaw != None:
        for child in MeshListRaw:
            if child.find("DescriptorName", {'MajorTopicYN':'Y'}) != None:
                MeshList.append(child.contents[0].attrs["UI"].strip())
    
      

    if(len(MeshList) == 0):
        MeshList.append('x')

    return ';'.join(MeshList)   

'''
    Function to process group all the necessary information of an article and add it to a Dataframe. 
    -> Clean the text.
    -> Organize information in a temporal list.  

    Input: articleInfo_xml -> A BeautifulSoup parser with all the information of an article
           temp -> A list with the information of a batch of processed articles. The information of the processed articles will be stored in this list.
           temp_errors -> A list with the ids of failed to process articles. If the article fails to be processed its id will be stored in this list.
    
    Output: A new row added to the temp list or the temp_errors list
'''


def process_article(articleInfo_xml,temp,temp_errors):
    id="_"
    error_code = ['.','.','.','.']
    try:
        #print("Start ",i)
        id = getXMLData(articleInfo_xml,"PMID")
        raw_title = getXMLData(articleInfo_xml,"ArticleTitle")
        raw_abstract = getXMLData(articleInfo_xml,"AbstractText")
        MeshTerm_string = getMeshTerms(articleInfo_xml)
        
        raw_text = raw_title +" "+ raw_abstract
        
        if(id == 'x' or raw_title == 'x' or raw_abstract == 'x' or MeshTerm_string == 'x'):
            if id == 'x': error_code[0] = 'x'
            if raw_title == 'x': error_code[1] = 'x'
            if raw_abstract == 'x': error_code[2] = 'x'
            if MeshTerm_string == 'x': error_code[3] = 'x'
            raise Exception("Not complete information"+''.join(error_code))
        
        clean_text = clean(raw_text)

        temp.append([id,clean_text,MeshTerm_string])
        
    except Exception as e:
        try:
            if id != "_":
                temp_errors.append([id,''.join(error_code)])
                #print(e)
            else:
                print(e)
            #print("Not possible to download ",articleInfo["PubmedArticle"][i]["MedlineCitation"]["PMID"])
        except Exception as ee:
            print(ee)
            #print("Not possible to download")
    
    

# =============================================================================
# Functions to download the data of the Pubmed articles 
# =============================================================================

Entrez.email = "nelsonquinones2424@gmail.com"
Entrez.api_key = "abd474bb98c9241472b3642237940f709307"

'''
    Function to bring Pubmed ids from articles since 2015 to 2022.

    Input:  start-> The article count from which the Query starts to retrieve the articles.
            size -> The amount of articles to retrieve in one query.

    Output: A list with Pubmed ids and metadata about the query.
'''

def getPubmedIds(start, size):
    can = False
    id_List = []
    while can == False:
        try:
            can = True
            handle = Entrez.esearch(db="pubmed",term = "2015/3/1:2022/4/30[Publication Date]",retmode="xml",retstart = start, Retmax = size)
            id_List = Entrez.read(handle)
            handle.close()
        except Exception as e:
            can = False
            time.sleep(0.5)
            print(e)

    return id_List


'''
    Function to bring articles information from Pubmed ids with a XML parser.

    Input:  id_List-> A list of pubmed ids.

    Output: A List with the information of the Pubmed articles in a XML parser.
'''
def getArticlesData(id_List):
    can = False
    Bs_data = None
    while can == False:
        try:
            can = True
            handle = Entrez.efetch(db="pubmed",id = ",".join(id_List), retmode="xml")
            articles_List_raw = handle.read()
            
            Bs_data = BeautifulSoup(articles_List_raw, "xml")
        except Exception as e:
            time.sleep(0.5)
            can = False
            print(e)

    return Bs_data.find("PubmedArticleSet")

'''
    Function to download all the Pubmed titles and abstracts from articles since 2015 to 2022

    Input:  
    Output: 
'''

def download():
    for xx in range(1,7):

        df_errors = pd.DataFrame(columns=["PMID","Reason"])
        errors_id = 0

        test_file_destiny = "data\\output\\"
        df = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms"])
        
        return_start = 6700000
        query_batch_size = 100
        batch_size = 100000

        article_cnt = return_start+((xx-1)*batch_size)
        thread_size = 5
        dataset_size = return_start+((xx)*batch_size)
        
        print(article_cnt,dataset_size)

        while article_cnt< dataset_size:
            #Get PubMed all pubmed ids from 2015 to today
            
            id_List = getPubmedIds(article_cnt,query_batch_size)

            article_cnt = article_cnt+query_batch_size
            
            #print(",".join(id_List['IdList']))
            #print(id_List['IdList'])
            
            article_List = getArticlesData(id_List['IdList'])

            my_threads = []

            temp = []
            temp_errors = []
            

            for i in article_List:
                #Process sequential
                process_article(i,temp,temp_errors)
                
                #Process in parallel
                # if len(my_threads) < thread_size:
                #     #print("This is f: ",f)
                #     new_thread = Thread(target=process_article, args=(i,temp,temp_errors))
                #     new_thread.start()
                #     my_threads.append(new_thread)
                # else:
                #     while len(my_threads) == thread_size:
                #         #print(f)
                #         #time.sleep(0.1)
                #         my_threads = [thread for thread in my_threads if thread.is_alive()]
                #     new_thread = Thread(target=process_article, args=(i,temp,temp_errors))
                #     new_thread.start()
                #     my_threads.append(new_thread)
            



            temp_df = pd.DataFrame(temp,columns =  ["PMID","Title/Abstract", "MeshTerms"])
            temp_df_error = pd.DataFrame(temp_errors, columns =  ["PMID","Reason"])

            df = pd.concat([df,temp_df])
            df_errors = pd.concat([df_errors,temp_df_error])
            
            print(article_cnt)
            

                
        #time.sleep(0.5)
        print(df.head())
        print(batch_size,thread_size)
        df.reset_index()
        df_errors.reset_index()
        df.to_csv(test_file_destiny+"\\Dataset_"+str(dataset_size)+"_.tsv", sep="\t")
        df_errors.to_csv(test_file_destiny+"\\Dataset_errors_"+str(dataset_size)+"_.tsv", sep="\t")

start_time = time.time()
download()
print("--- %s seconds ---" % (time.time() - start_time))