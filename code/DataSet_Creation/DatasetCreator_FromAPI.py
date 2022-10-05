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
    Function to process group all the necessary information of an article and add it to a Dataframe. 
    -> Clean the text.
    -> Organize information in the dataframe.  

    Input:  id -> A string with the Pubmed id that identifies the article.
            txt -> The text that contains the title and abstract of the article.
            mesh_terms -> The ids of the Mesh_terms of the article
    Output: A new row added to the articles Dataframe
'''


def process_article(summaries,i,temp,temp_errors):
    major_topics_cnt = 0
    try:
        #print("Start ",i)
        id = summaries["PubmedArticle"][i]["MedlineCitation"]["PMID"]
        raw_text = "".join(summaries["PubmedArticle"][i]["MedlineCitation"]["Article"]["Abstract"]["AbstractText"])
        raw_text = summaries["PubmedArticle"][i]["MedlineCitation"]["Article"]["ArticleTitle"].join(raw_text)
        clean_text = clean(raw_text)
        #print(clean_text)

        #MeshTerms
        #print("Keyword list: ")
        keywords_string = ""
        keywords_list = []
        if(len(summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"])>0):
            #print(summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"])
            for keyword in summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"][0] :
                #print(keyword,keyword.attributes["MajorTopicYN"])
                if(keyword.attributes["MajorTopicYN"] == 'Y'):
                    keywords_list.append(keyword)
                    major_topics_cnt = major_topics_cnt+1
        
        keywords_string = ",".join(keywords_list)
        #print(keywords_string)
        
        if(major_topics_cnt == 0):
            raise Exception("No Mesh_terms available")

        temp.append([id,clean_text,keywords_string])
        #print("End ",i)
        #print()
    except Exception as e:
        try:
            temp_errors["PMID"].append(summaries["PubmedArticle"][i]["MedlineCitation"]["PMID"])
            
            #print(e)
            #print("Not possible to download ",summaries["PubmedArticle"][i]["MedlineCitation"]["PMID"])
        except Exception as ee:
            print(ee)
            #print("Not possible to download")
    
    

# =============================================================================
# Functions to download the data of the Pubmed articles 
# =============================================================================

'''
    API information to make queries to the BioC API.
'''
Entrez.email = "nelsonquinones2424@gmail.com"
Entrez.api_key = "abd474bb98c9241472b3642237940f709307"

'''
    Function to bring Pubmed ids from articles since 2015 to 2022.

    Input:  start-> The article count from which the Query starts to retrieve the articles.
            size -> The amount of articles to retrieve in one query.

    Output: A list with Pubmed ids and metadata about the query.
'''

def getPubmedIds(start, size):
    handle = Entrez.esearch(db="pubmed",term = "2015/3/1:2022/4/30[Publication Date]",retmode="xml",retstart = start, Retmax = size)
    records = Entrez.read(handle)
    handle.close()
    return records


'''
    Function to bring articles information from Pubmed ids.

    Input:  records-> A list of pubmed ids.

    Output: A dictionary with information like title,abstract, meshterms, etc; from the articles with the given Pubmed Ids.
'''
def getArticlesData(records):
    handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']), retmode="xml")
    summaries = Entrez.read(handle)
    handle.close()
    return summaries

'''
    Function to download all the Pubmed titles and abstracts from articles since 2015 to 2022

    Input:  
    Output: 
'''

def download():
    for xx in range(1,15):

        df_errors = pd.DataFrame(columns=["PMID"])
        errors_id = 0

        test_file_destiny = "data\\output\\"
        df = pd.DataFrame(columns =  ["PMID", "Title/Abstract", "MeshTerms"])
        
        return_start = 5000000
        query_batch_size = 100
        batch_size = 100

        article_cnt = return_start+((xx-1)*batch_size)
        thread_size = 5
        dataset_size = return_start+((xx)*batch_size)
        
        print(article_cnt,dataset_size)

        while article_cnt< dataset_size:
            #Get PubMed all pubmed ids from 2015 to today
            
            records = getPubmedIds(article_cnt,query_batch_size)

            article_cnt = article_cnt+query_batch_size
            
            #print(",".join(records['IdList']))

            summaries = getArticlesData(records['IdList'])

            my_threads = []

            temp = []
            temp_errors = {"PMID":[]}
            

            for i in range(query_batch_size):
                #Process sequential
                process_article(summaries,i,temp,temp_errors)
                
                # Process in parallel
                # if len(my_threads) < thread_size:
                #     #print("This is f: ",f)
                #     new_thread = Thread(target=process_article, args=(summaries,i,temp,temp_errors))
                #     new_thread.start()
                #     my_threads.append(new_thread)
                # else:
                #     while len(my_threads) == thread_size:
                #         #print(f)
                #         #time.sleep(0.1)
                #         my_threads = [thread for thread in my_threads if thread.is_alive()]
                #     new_thread = Thread(target=process_article, args=(summaries,i,temp,temp_errors))
                #     new_thread.start()
                #     my_threads.append(new_thread)
            



            temp_df = pd.DataFrame(temp,columns =  ["PMID","Title/Abstract", "MeshTerms"])
            temp_df_error = pd.DataFrame(temp_errors)

            df = pd.concat([df,temp_df])
            df_errors = pd.concat([df,temp_df_error])
            
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