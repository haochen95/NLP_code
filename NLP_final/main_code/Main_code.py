#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xlrd
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
import gensim
from gensim.models import Word2Vec
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models, similarities
import os
import csv
import pandas

# ======================================================================= ###
# ------------------>>>>> PART 3  Query process <<<<<---------------------- ##

# (1) input query

def preprocess(text, selected_stopwords = []):  # into [' I am of ok'] ---->>>> ['i','am','ok']
    # remove the punctuation and tokenize to word
    lowers = text.lower()
    lemmatizer = WordNetLemmatizer()
    filtered = []
    stop_words = set(selected_stopwords)
    no_punctuation = re.sub('[%s]' % string.punctuation, '', lowers)
    tokens = nltk.word_tokenize(no_punctuation)
    # remove stopwords and lemma
    for words in tokens:
        if words not in stop_words:
                filtered.append(lemmatizer.lemmatize(words))
    return filtered

rooter = os.path.abspath(os.path.dirname(os.getcwd()))

from nltk.corpus import wordnet as wn
orginal_query = input('Please Enter a Query :    ')
processed_original_query = preprocess(orginal_query, stopwords.words('english'))

construction_model = Word2Vec.load( rooter + "\\postdata_corpus_model\\trained_model\\trained_model" )

# (5) expand keywords
vocabulary =[]
for word, vocab_obj in construction_model.wv.vocab.items():
    vocabulary.append(word)

standard_keyword =[]
with open( rooter + '\\postdata_corpus_model\\keywords\\pre_keywords.txt', 'r' ) as std_keywords:
    for words in std_keywords.readlines():
        standard_keyword.append(words)

lexicon_dict = dict()
for word in standard_keyword:
    p_word = word.strip('\n')
    if p_word in vocabulary:
        for res in construction_model.most_similar(p_word, topn = 5):
            lexicon_dict.setdefault(p_word, []).append(res[0])
            # lexicon_dict[p_word] = (res[0])  # save keyword - similarity word
    else:
        lexicon_dict[p_word] =[]

key_word = []
for keys in lexicon_dict:
    key_word.append(keys)

# (2) expand processed_query
def expand_query(key_word, processed_original_query,lexicon_dict):  # keyword of construction, lexicon_dict is expanded keyword lexion
    expand_a =dict()
    for words in processed_original_query:
        if words not in key_word:   # words not in lexicon
            for l in wn.synsets(words):
                for k in l.lemmas():
                    expand_a.setdefault(words, [])
                    if k.name() not in expand_a[words]:
                    # expand_a[words].append(k.name())
                        expand_a[words].append(k.name())
        else:    # words in lexicon
            expand_a[words] = lexicon_dict[words]
            # expand_a.setdefault(words, []).append(lexicon_dict[words])
    return expand_a

expand_all = expand_query(key_word, processed_original_query, lexicon_dict)


# （3） Filter out words from vocabulary
#  3.1 load model and compute model vocabulary

vocabulary =[]
for word, vocab_obj in construction_model.wv.vocab.items():
    vocabulary.append(word)

# 3.2 filter out query and expand-query words that doesn's exist in vocabulary
def filter_out_words(vocabulary, processed_original_query, pand_query):
    for terms in processed_original_query:
        if terms in vocabulary:
            continue
        else:
            processed_original_query.remove(terms)

    for key, term in pand_query.items():
        for x in term:
            if x in vocabulary:
                continue
            else:
                pand_query[key].remove(x)

    return processed_original_query, pand_query

final_original_query, final_expand_query = filter_out_words(vocabulary, processed_original_query, expand_all)

for k,v in final_expand_query.items():
    print(k,v)
# ======================================================================= #
# ------------------>>>>> PART 3  Compute TF-IDF scores <<<<<---------------------- #

# (1) load corpus model
dictionary_final = corpora.Dictionary.load( rooter + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.dict' )
corpus_final = corpora.MmCorpus( rooter + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.mm' )

tfidf_model = models.TfidfModel(corpus_final)   # train a TF-IDF model using corpus
corpus_tfidf = tfidf_model[corpus_final]       # apply trained TF-IDF model to corpus
standard_dictionary = list(dictionary_final.token2id.keys())

# (2) cosine-based similarity calculate set up
index_tfidf = similarities.MatrixSimilarity(corpus_tfidf)
# index_tfidf.num_best = 5     # top 5 similarity

# (3) give a score
final_expand_post_query =[]
for item in list(final_expand_query.values()):
    for words in item:
        final_expand_post_query.append(words)

score_orignal = index_tfidf[tfidf_model[dictionary_final.doc2bow(final_original_query)]]
score_expand = index_tfidf[tfidf_model[dictionary_final.doc2bow(final_expand_post_query)]]

print(score_orignal)
print(score_expand)

ranking_original_list = list(enumerate(score_orignal))
ranking_expand_list = list(enumerate(score_expand))
final_result =[]

for doc in range(len(ranking_original_list)-1):
    fax = ranking_original_list[doc][1] + 0.7 * ranking_expand_list[doc][1]
    final_result.append((doc+1, round(fax, 10)))

sorted_result = final_result.sort(key = lambda x:x[1], reverse=True)       # rank results

# print("Final Result\n\n\n\n")
for k in final_result[:20]:
    print(k)

ranked_index = []
prob_list = []
content_info = []

for i in final_result:
    ranked_index.append(i[0])
    prob_list.append(i[1])

with open(rooter + "\\risk_case.csv", 'r') as f:
    readcsv = csv.reader(f)
    rows = [r for r in readcsv]

for index in ranked_index:
    content_info.append(rows[index-1][0])

data_final = {'Case index':ranked_index,
              'Similarity':prob_list,
              'Case description':content_info}
frame = pandas.DataFrame(data_final, columns=['Case index','Similarity', 'Case description' ])
print(frame)
writer = pandas.ExcelWriter(rooter + '\\Final_Score_Result.xlsx')
frame.to_excel(writer, 'Results', index = False)
writer.save()
