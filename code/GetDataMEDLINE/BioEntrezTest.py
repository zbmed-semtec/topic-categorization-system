from pdb import Restart
import Bio
from Bio import Entrez
import re, nltk
from nltk.stem.snowball import SnowballStemmer

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

#Get PubMed all pubmed ids from 2015 to today
Entrez.email = "nelsonquinones2424@gmail.com"
Entrez.api_key = "abd474bb98c9241472b3642237940f709307"
handle = Entrez.esearch(db="pubmed",term = "2015/3/1:2022/4/30[Publication Date]",retmode="xml",retstart = 40, Retmax = 20)
records = Entrez.read(handle)
handle.close()

print(records['Count'])
print(records['IdList'])
print(",".join(records['IdList']))
handle = Entrez.efetch(db="pubmed",id = ",".join(records['IdList']), retmode="xml")
summaries = Entrez.read(handle)
handle.close()

batch_size = 20
start = 0



for i in range(19):
    #Title

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
        for key_word in summaries["PubmedArticle"][i]["MedlineCitation"]["KeywordList"][0]:
            print(key_word)
    
    else:
        print("No keyword.")
    print()