from newspaper import Article
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import numpy as np
import warnings
import string


warnings.filterwarnings('ignore')


nltk.download('punkt' , quiet=True)
nltk.download('wordnet' , quiet=True)

article = Article('https://en.wikipedia.org/wiki/SpaceX')
article.download()
article.parse()
article.nlp()
corpus = article.text

text = corpus
sent_tokens = nltk.sent_tokenize(text)

remove_punct_dict = dict( (ord(punct),None) for punct in string.punctuation)

def LemNormalize(text):
    return nltk.word_tokenize(text.lower().translate(remove_punct_dict))


GREETING_INPUTS=["hi","hello","hola","greetings","wassup","hey"]
GREETING_RESPONSE=["howdy","hi","hey","what's good","hello","hey there"]

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSE)

def response(user_response):
    user_response = user_response.lower()
    robo_response = ''        
    sent_tokens.append(user_response)
    TfidfVect = TfidfVectorizer(tokenizer = LemNormalize, stop_words='english')
    tfidf = TfidfVect.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1],tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    score = flat[-2]

    if(score == 0):
        robo_response = robo_response+" I don't understand"
    else:
        robo_response = robo_response+sent_tokens[idx]    
    sent_tokens.remove(user_response)    
    return robo_response

flag = True
while(flag == True):
    user_response = input()
    user_response = user_response.lower()
    if(user_response != 'bye'):
        if(user_response == 'thanks' or user_response=='thank you'):
            flag = False
            print("You are welcome")
        else:
            if(greeting(user_response)!=None):
                print(greeting(user_response))
            else:
                print(response(user_response))
                    
    else:
        flag = False
        print("Bubye")


 


