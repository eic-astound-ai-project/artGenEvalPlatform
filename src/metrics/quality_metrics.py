import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from gensim.models import KeyedVectors
from pyemd import emd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import nltk
from nltk.translate.bleu_score import sentence_bleu
from sentence_transformers import SentenceTransformer
# from nlg_eval import compute_metrics
# #import fasttext
#
#
# def calculate_rouge(reference, hypothesis):
#     metrics = compute_metrics(hypothesis, [reference], no_skipthoughts=True, no_glove=True)
#     rouge_scores = metrics['rouge']
#     print(rouge_scores)
#     return rouge_scores


def cos_similarity(vector1, vector2):
    """
    This metric calculates the cosine angle between two
    sentence vectors and can give a score between -1 and 1 to indicate the similarity between two sentences.
    :param sentence1:
    :param sentence2:
    """

    # Calculate cosine similarity between the vectors
    cosine_sim = cosine_similarity([vector1], [vector2])[0][0]

    print("Cosine similarity:", cosine_sim)
    return cosine_sim

def jacard_similarity(sentence1, sentence2):
    """
    This metric measures the similarity between sets of words in two sentences.
    It calculates the intersection over the union of the two sets of words to give a score between 0 and 1.
    :param sentence1:
    :param sentence2:
    """
    # Convert sentences to sets of words
    words1 = set(sentence1.split())
    words2 = set(sentence2.split())

    # Calculate Jaccard similarity between the sets
    jaccard_sim = len(words1.intersection(words2)) / len(words1.union(words2))

    print("Jaccard similarity:", jaccard_sim)
    return jaccard_sim


def accuracy(reference_sentence, generated_sentence):
    """
        This metric measures whether the generated sentence contains the same words that the reference sentence
        It calculates the intersection over the reference of the two sets of words to give a score between 0 and 1.
        :param sentence1:
        :param sentence2:
        """
    # Convert sentences to sets of words
    reference_words = set(reference_sentence.split())
    generated_words = set(generated_sentence.split())

    # Calculate Jaccard similarity between the sets
    acc = len(reference_words.intersection(generated_words)) / len(reference_words)

    print("Accuracy:", acc)
    return acc



def levenshtein_dist(sentence1, sentence2):

    """
    This metric calculates the number of insertions, deletions, and substitutions required
    to transform one sentence into another. The lower the distance, the more similar the sentences
    Alternative implementation: https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
    :param sentence1:
    :param sentence2:
    """
    # Calculate Levenshtein distance between the sentences
    lev_dist = Levenshtein.distance(sentence1, sentence2)

    # Normalize distance to get similarity score
    lev_sim = 1 - (lev_dist / max(len(sentence1), len(sentence2)))

    print("Levenshtein similarity:", lev_sim)
    return lev_sim

def wordMoves_dist(model, sentence1, sentence2):
    """
    Word Mover's Distance (WMD): This metric calculates the minimum distance
    between the words in two sentences, taking into account the semantic relationships between words
    :param sentence1:
    :param sentence2:
    """
    # Load pre-trained word embedding model (e.g. Word2Vec or GloVe)
    model = KeyedVectors.load_word2vec_format('path/to/model.bin', binary=True)

    # Convert sentences to lists of word vectors
    list1 = [model[word] for word in sentence1.split()]
    list2 = [model[word] for word in sentence2.split()]

    # Calculate Word Mover's Distance between the lists
    wmd = emd(list1, list2, model.wv.vocab)

    print("Word Mover's Distance:", wmd)

def latent_semantic_analysis(sentence1, sentence2):
    """
    NOT READY YET > TO BE TRAINED IF NEEDED
    Latent Semantic Analysis (LSA): This technique uses Singular Value Decomposition (SVD)
     to identify latent semantic factors in a corpus of text.
     It can be used to compare the semantic similarity between two sentences.
    :param sentence1:
    :param sentence2:
    """
    # Convert sentences to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([sentence1, sentence2])

    # Apply Latent Semantic Analysis (LSA)
    lsa = TruncatedSVD(n_components=2)
    vectors_lsa = lsa.fit_transform(vectors)
    # Calculate cosine similarity between the LSA vectors
    cosine_sim = cosine_similarity([vectors_lsa[0]], [vectors_lsa[1]])[0][0]
    print("Latent Semantic Analysis similarity:", cosine_sim)


def BLEUn(reference, translation, weights=(0.25, 0.25, 0.25, 0.25)):
    """
    BLEU measures the similarity between the machine-generated translation and one or more reference translations.
    It does this by comparing n-grams (sequences of n words) in the machine-generated translation to n-grams in the reference translations.
    The score ranges from 0 to 1, with a higher score indicating better quality translation.
    The lenght of the n-gram will be indicated in the number of weights.
    In general, larger n-grams capture longer-range dependencies between words, while smaller n-grams capture more local relationships.
    BLEU-4 is a commonly used choice for machine translation evaluation, as it has been found to correlate well with human judgments of translation quality.
    However, for other tasks, such as sentence similarity evaluation, smaller n-grams may be more appropriate.
    :param reference:
    :param translation:
    :param weights:
    """
    # Tokenize the sentences
    if(isinstance(weights, str)):
        weights = eval(weights)
    reference_tokens = nltk.word_tokenize(reference)
    translation_tokens = nltk.word_tokenize(translation)

    # Calculate the BLEU score with 4-gram (BLEU-4)
    bleu_score = sentence_bleu([reference_tokens], translation_tokens, weights=weights)
    #print("BLEU score:", bleu_score)
    return bleu_score




def WER(reference, hypothesis):
    """
   #     WER stands for Word Error Rate, and it is a metric commonly used to evaluate the performance of automatic speech recognition (ASR) systems
   #     The WER measures the difference between the reference transcription (i.e., the ground truth text)
   #     and the output of the ASR system in terms of the number of word errors.
   #     It is defined as the ratio of the total number of word substitutions, deletions, and insertions in the ASR output,
   #     divided by the total number of words in the reference transcription.
   #     The WER is typically expressed as a percentage, with lower values indicating better performance.
   #     For example, a WER of 5% means that there were, on average, 5 errors per 100 words in the ASR output.
   #     :param reference:
   #     :param hypothesis:
   #     """
    # Ref:
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    # Counting the number of substitutions, deletions, and insertions
    substitutions = sum(1 for ref, hyp in zip(ref_words, hyp_words) if ref != hyp)
    deletions = len(ref_words) - len(hyp_words)
    insertions = len(hyp_words) - len(ref_words)
    # Total number of words in the reference text
    total_words = len(ref_words)
    # Calculating the Word Error Rate (WER)
    wer = (substitutions + deletions + insertions) / total_words
    print("WER:", wer)
    return wer


def semanticSimilarity(reference_sentence, generated_sentence, similarity_metric="cosineSim", tokensGenerator="all-MiniLM-L6-v2"):
    model = load_model(model_name = tokensGenerator)
    semanticEmbs_reference_sentence = get_embs_from_tokens(model, reference_sentence)
    semanticEmbs_generated_sentence = get_embs_from_tokens(model, generated_sentence)
    if(similarity_metric=="cosineSim"):
        semanticDist = cos_similarity(semanticEmbs_reference_sentence, semanticEmbs_generated_sentence)
    else:
        print("Type of similarity metric ", similarity_metric, " not-recognized. Try: 'cosineSim'")
        semanticDist = -1
    return float(semanticDist)



def load_model(model_name = "all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)


def get_embs_from_tokens(model, sentence):
    # Apply average pooling to combine embeddings of the different tokens of a sentence
    query_embedding = model.encode(sentence)
    return query_embedding



def metrics_calculator(metric_name, reference_sentence, generated_sentence, extra_params={}):
    if(metric_name=="WER"):
        score = WER(reference_sentence, generated_sentence)
    elif("BLEU" in metric_name):
        score = BLEUn(reference_sentence, generated_sentence, **extra_params)
    elif(metric_name=="JaccardSim"):
        score = jacard_similarity(reference_sentence, generated_sentence)
    elif(metric_name=="accuracy"):
        score = accuracy(reference_sentence, generated_sentence)
    elif(metric_name=="levhensteinDist"):
        score = levenshtein_dist(reference_sentence, generated_sentence)
    elif(metric_name=="semanticSim"):
        score = semanticSimilarity(reference_sentence, generated_sentence, **extra_params)
    else:
        print("Type of metric ", metric_name, " not-recognized. Try: ['WER', 'BLEU', 'JaccardSim', 'accuracy', "
                                              "'levhensteinDist', 'semanticSim']. Returned value for metric: -1")
        score = -1
    return score




#### FAST TEXT #### https://fasttext.cc/docs/en/unsupervised-tutorial.html
# def load_model(path_model_fasttext):
#     return fasttext.load_model(path_model_fasttext)
#
# def check_similar_families(model, word):
#     # Semantic level & miss-speled
#     model.get_nearest_neighbors(word)
#     # analogies
#     model.get_analogies("berlin", "germany", "france") #Expected paris
#
# def predict_tokens(model, sentence):
#     data = []
#     tokens = sentence.rstrip().split(' ')
#     for token in tokens:
#         data+=[model.get_word_vector(token)]
#     return data




if __name__ == '__main__':
    # skip weird characters, lowercase, ..
    sentence1 = "Portrait of Madame Ginoux l'Arlesienne 1890"#.lower().replace("'", " ")
    sentence2 = "Portrait of madame ginoux l arlesienne 1890"#.lower()
    print("BLEU-1")
    print(BLEUn(sentence1, sentence2,  weights=(1, 0, 0, 0)))
    print("BLEU-4")
    print(BLEUn(sentence1, sentence2))


    sentence1 = "The cat is sleeping on the mat."
    sentence2 = "The cat is playing on mat."
    print("WER")
    WER(sentence1, sentence2)
    print("WER2")
    calculate_wer(sentence1, sentence2)

    print("LEVENSHTEIN")
    levenshtein_dist(sentence1, sentence2)
    print("Jaccard")
    jacard_similarity(sentence1, sentence2)
    print("ROUGE")
    #calculate_rouge(sentence1, sentence2)

    print("Cosine Similarity")
    #model = load_model(model_name="all-MiniLM-L6-v2")
    #embs1 = get_embs_from_tokens(model, sentence1)
    #embs2 = get_embs_from_tokens(model, sentence2)
    #cos_similarity(embs1, embs2)








