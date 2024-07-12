import functools
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string

def extreme_processing(sentence):
    tokens = word_tokenize(sentence.strip())
    # convert to lower case
    tokens = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    return words


def stemming_words(sentence):
    #Stemming refers to the process of reducing each word to its root or base.
    porter = PorterStemmer()
    tokens = word_tokenize(sentence)
    stemmed = [porter.stem(word) for word in tokens]
    return stemmed


class Text_processor:
    def __init__(self, mapping_words2repl, lowercase):
        self.mapping_words2repl = mapping_words2repl
        if(isinstance(lowercase, str)):
            self.lowercase = eval(lowercase)
        else:
            self.lowercase = lowercase

    def preprocessing_text(self, initial_text):
        processedText = str(initial_text)
        if(self.lowercase):
            processedText = processedText.lower()
        try:
            processedText = functools.reduce(lambda a, kv: a.replace(*kv), self.mapping_words2repl.items(), processedText)
        except AttributeError:
            pass
        return processedText



def str_parser(response, parser="\n\n"):
    return response.split(parser)


def splitWords(list2split, parser=" "):
    splitted_list = []
    for words in list2split:
        yield from words.split(parser)




def convert_profile_list2dict(listOfProfiles, textProcessor): #maybe it is possible to do this recursive
    profilesAsdict = {}
    for profile in listOfProfiles:
        profilesAsdict[
            textProcessor.preprocessing_text(profile["profile_name"])] = subprocess_fieldsOfprofile(profile["profile_fields_prompt"], textProcessor)
    return profilesAsdict



def subprocess_fieldsOfprofile(profile_fields, textProcessor):
    processed_fields = {}
    for field_name in profile_fields:
        processed_fields[textProcessor.preprocessing_text(field_name)] = textProcessor.preprocessing_text(profile_fields[field_name])
    return processed_fields



