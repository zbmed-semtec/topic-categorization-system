from article_finder import getArticleData
from flask import Flask, request
from flask_cors import CORS
import re, nltk
from nltk.stem.snowball import SnowballStemmer
import model

# nltk dependencies
nltk.download('stopwords') #required 
nltk.download('punkt') #required

stemmer = SnowballStemmer("english")
stopword_list = nltk.corpus.stopwords.words('english')
stopword_list = stopword_list + ['']


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
#print(getArticleData(34694464))

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


@app.route("/<int:id>")
def get_article_data(id):
    return getArticleData(id)

@app.route('/predict', methods=['POST'])
def json_example():
    request_data = request.get_json()

    title = request_data['title']
    abstract = request_data['abstract']
    raw_text= title +" "+ abstract
    clean_text = clean(raw_text)
    res = {}
    binary, types = model.predict(clean_text)
    res["binary"] = binary
    res["types"] = types
    return res


app.run(debug=True)

#print(model.predict('limit use dithionit quench determin topolog membran insert protein determin topolog membran insert protein peptid often reli upon indirect fluoresc measur one techniqu use nbd environment sensit fluorophor coval link protein relat hydrophil environ nbd hydrophob environ show increas emiss intens shift shorter wavelength gain insight nbd fluoresc chemic quench use dithionit dithionit anion expect penetr outer leaflet interfaci region exclud hydrocarbon core inner leaflet lumen luv assumpt hold neutral ph larg number nbddithionit experi carri report control experi luv direct label nbd pe assess dithionit'))