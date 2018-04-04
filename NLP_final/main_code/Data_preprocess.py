# ======================================================================= #
# ------------------>>>>> PART 1  Risk case processing <<<<<--------------- #

# (1) convert text file(crawled from OSHA website 24321 cases) into csv file
import csv
import gensim
from gensim import corpora
from gensim.models import Word2Vec
from nltk import FreqDist, WordNetLemmatizer
from nltk.corpus import stopwords
import os

import nltk
import string
import re
import sys
import logging

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

koo = input("Please enter the keywords you being used to crawl data from OSHA-------->>>")
root_path = os.path.abspath(os.path.dirname(os.getcwd()))


with open( root_path + '\\risk_case.csv', 'w', newline='' ) as csvfile:
    writer = csv.writer(csvfile)
    with open(root_path + "\\Crawl_cases_from_OSHA\\" + koo.replace(' ','').lower() + '.txt', 'r') as textfile:
            for line in textfile:
                writer.writerow([line.strip('\n')])

# (2) Read risk cases and pre-process context:
#  2.1 process data (without custom stopwords)
with open( root_path + '\\risk_case.csv', 'r' ) as open_data:
    readcsv = csv.reader(open_data)
    raw_data = []   # without pre-process
    preprocess_data =[] # preprocessed
    for row in readcsv:
        raw_data.append(row[0])
        preprocess_data.append(preprocess(row[0], stopwords.words('english')))

#  2.2 find top 200 stopwords and manually select meaningless stopwords
flat_data = [item for sublist in preprocess_data for item in sublist]   # combine into one list
fdist = FreqDist(flat_data)
selected = fdist.most_common(200)
with open( root_path + '\\postdata_corpus_model\\post_data\\top_200_frequency_words_stopwords.txt', 'w' ) as sel:  # store selected stopwords
    for std in selected:
        sel.write(' '.join(str(s) for s in std) + '\n')

# manually select stopwords and build file names 'case_stopwords.txt'
with open( root_path + '\\postdata_corpus_model\\post_data\\english_stopwords.txt', 'w' ) as eng:
    for words in stopwords.words('english'):
        eng.write(words + '\n')

# 2.3 Select words that appear only two times
with open( root_path + '\\postdata_corpus_model\\post_data\\less_than_2_times_stopwords.txt', 'a' ) as less:
    res = list(filter(lambda x: x[1]<=2, fdist.items()))
    nes = [x[0] for x in res]
    for m in nes:
        less.write(''.join(str(m)) + '\n')

yes = {"y","yes"}
no = {"n","no"}

while True:
    try:
        done = input("Have you create ''manually_selected_stopwords.txt'' ? [yes/no]")
    except EOFError:
        print("Sorry, I didn't understand that.")
        continue

    if done.strip().lower() in yes:
        break # leave while
    elif done.strip().lower() in no:
        # do part one again
        print("Doing part 1")
        pass
    else:
        # neither yes nor no, back to question
        print("Sorry, I didn't understand that.")



# =======================================================================
# # manually select stopwords and build file names 'case_stopwords.txt'
#=========================================================================




# Overall stopwords:
file_names = ['english_stopwords.txt','less_than_2_times_stopwords.txt','manually_selected_stopwords.txt']
with open( root_path + '\\postdata_corpus_model\\post_data\\overall_case_stopwords.txt', 'w' ) as outfile:
    for fname in file_names:
        with open( root_path + '\\postdata_corpus_model\\post_data\\' + fname ) as infile:
            for line in infile:
                outfile.write(line)

#  2.4 After stopwords selected, run pre-process method again:
selected_stopwords =[]
with open( root_path + '\\postdata_corpus_model\\post_data\\overall_case_stopwords.txt', 'r' ) as l:
    for line in l.readlines():
        selected_stopwords.append(''.join(line.strip('\n').split()))

post_process_data =[]
for x in raw_data:
    post_process_data.append(preprocess(x, selected_stopwords))

# (3) build dictionary and save
dictionary = corpora.Dictionary(post_process_data)
print(dictionary.token2id)   #[('a',1), ('b',2), ('c',3)]
dictionary.save( root_path + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.dict' )  # give each words with a id to build dictionary

# (4) build corpus and save
corpus = [dictionary.doc2bow(text) for text in post_process_data]
corpora.MmCorpus.serialize( root_path + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.mm', corpus )  # save corpus


# ======================================================================= #
# ---->>>>> PART 2  Keyword pre-process and train Word2Vec model <<<<<----- #

# (1) import dictionary and corpus
dictionary = corpora.Dictionary.load( root_path + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.dict')
corpus = corpora.MmCorpus(root_path + '\\postdata_corpus_model\\dictionary_corpus\\risk_case.mm' )
standard_dictionary = list(dictionary.token2id.keys())

# (2) process risk-keywords
case_keyword = []
with open( root_path + '\\postdata_corpus_model\\keywords\\raw_keyword.txt', 'r' ) as risk_keyword:
    for line in risk_keyword:
        new_line = line.replace(';', ' ')
        case_keyword.append(new_line.split())
long_words =[]
for x in case_keyword:
    for words in x:
        long_words.append(words.lower())
long_words = list(set(long_words))
lemmatizer = WordNetLemmatizer()
with open( root_path + '\\postdata_corpus_model\\keywords\\pre_keywords.txt', 'w' ) as pre_key:
        for words in long_words:
                if words not in stopwords.words('english'):
                    pre_key.write(lemmatizer.lemmatize(words) +'\n')

while True:
    try:
        done = input("You can add more construction-related keywords in pre-keyword.txt file, Type yes to continue [yes/no]")
    except EOFError:
        print("Sorry, I didn't understand that.")
        continue

    if done.strip().lower() in yes:
        break # leave while
    elif done.strip().lower() in no:
        pass
    else:
        # neither yes nor no, back to question
        print("Sorry, I didn't understand that.")


while True:
    try:
        done = input("You're going to train Word2Vec model, Be prepare as it takes some time [yes/no]")
    except EOFError:
        print("Sorry, I didn't understand that.")
        continue

    if done.strip().lower() in yes:
        break # leave while
    elif done.strip().lower() in no:
        pass
    else:
        # neither yes nor no, back to question
        print("Sorry, I didn't understand that.")


# (3) train word2vec model
# 3.1 open raw text
with open( root_path + '\\dataset\\final_data.txt', 'r' ) as my_file:
    sentences = my_file.read().splitlines()
    sentences_splitted = [elt.split() for elt in sentences]

    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

model = gensim.models.Word2Vec(sentences_splitted,
                                window=5,  # default
                                size=300,  # dimensionality of the word vectors
                                workers=4,  # number of cores to use
                                iter=15,  # more is better
                                sample=1e-3,  # default, subsampling threhsold
                                negative=5,  # default, number of negative examples for each positive one
                                sg=1)  # skip-gram
# when training is done
model.init_sims(replace=True)
model.save( root_path + "\\postdata_corpus_model\\trained_model\\trained_model" )

# ============================================================= ##
# (4) at this time, we first use their model
# ============================================================= ##
construction_model = Word2Vec.load( root_path + "\\postdata_corpus_model\\trained_model\\trained_model" )

# (5) expand keywords
vocabulary =[]
for word, vocab_obj in construction_model.wv.vocab.items():
    vocabulary.append(word)

standard_keyword =[]
with open(  root_path + '\\postdata_corpus_model\\keywords\\pre_keywords.txt', 'r' ) as std_keywords:
    for words in std_keywords.readlines():
        standard_keyword.append(words)

lexicon_dict = dict()
for word in standard_keyword:
    p_word = word.strip('\n')
    if p_word in vocabulary:
        for res in construction_model.most_similar(p_word, topn = 10):
            lexicon_dict.setdefault(p_word, []).append(res[0])
            # lexicon_dict[p_word] = (res[0])  # save keyword - similarity word
    else:
        lexicon_dict[p_word] =[]

# save expanded keyword into csv file
with open( root_path + '\\postdata_corpus_model\\keywords\\keyword_lexicon.csv', 'w', newline='' ) as lex:
    w = csv.writer(lex)
    for key, val in lexicon_dict.items():
        w.writerow([key, val])