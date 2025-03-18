import datetime
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

from files.porter import PorterStemmer


#
# This is code for small corpus
#


# TEXT PRE-PROCESSING

def clean_document(s):
    # normalisation: lowercase, delete full stops U.S.A, delete hyphens
    # cleaning documents
    s = s.lower()
    s = re.sub('  ', ' ', s)
    # delete hyphens
    s = re.sub('-', '', s)
    s = re.sub('_', '', s)
    s = re.sub(r"\'s", " ", s)
    s = re.sub('[()]', '', s)

    s = re.sub(r"won't", "will not", s)
    s = re.sub(r"can\'t", "can not", s)
    s = re.sub(r"n\'t", " not", s)
    s = re.sub(r"\'re", " are", s)
    # s = re.sub(r"\'s", " is", s)

    s = re.sub(r"\'d", " would", s)
    s = re.sub(r"\'ll", " will", s)
    s = re.sub(r"\'t", " not", s)
    s = re.sub(r"\'ve", " have", s)
    s = re.sub(r"\'m", " am", s)
    # digits
    s = re.sub(r'[0-9]+', '', s)
    # punctuations
    s = re.sub(r'[^\w]', ' ', s)
    s = re.sub(' +', ' ', s)
    s.replace("\n", " ").strip()

    return s


#  Extract the documents contained in the document collections provided.
#  This function outputs a dict containing cleaned raw text document.
def raw_texts_cleaning(docs_dir):
    doc_list = []
    file_name_list = []
    # Folder traversal
    for file_name in os.listdir(docs_dir):
        try:
            document_file_name = docs_dir + "/" + file_name
            # Open file in the folder
            with open(document_file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            file_name_list.append(file_name)
            # Record the content of the document after cleaning
            content = clean_document(content)
            clean_document(content).strip()
            doc_list.append(content)
        except:
            pass

    return doc_list, file_name_list


# Perform text_tokenization as well as stopword removal, and stemming
# This function returns a nested list containing tokenized terms
def text_tokenization(dl):
    doc_list = [doc.split(" ") for doc in dl]
    new_doc_list = []
    for index, doc in enumerate(doc_list):
        new_doc = []
        # Stem the word in each document
        for word in doc:
            # Do stop word removal and stemming
            if word in stopwords:
                continue
            # Words that are not stopwords are added to the new document
            word = poster_stemmer.stem(word)
            new_doc.append(word)

        new_doc_list.append(new_doc[0:-1])


    return new_doc_list

# The BM25 Model
class BM25(object):
    def __init__(self, docs, weights, file_name_list):
        if os.path.exists("w.txt"):
            print("loading weights")

            self.doc_num = weights["DocNum"]
            self.avg_doc_num = weights["AvgDocNum"]
            self.k1 = weights["K1"]
            self.b = weights["B"]
            print("loading term frequency")
            # with open("./term_frequency.txt", 'r') as f:
            #     self.term_f_dict = json.loads(f.read())
            self.term_f_dict = weights["TermFrequency"]

            print("loading inverted index")
            # with open("./inverted_index.txt", 'r') as f:
            #     self.inverted_index = json.loads(f.read())
            self.inverted_index = weights["InvertedIndex"]
            print("loading doc length")
            # with open("./doc_len.txt", 'r') as f:
            #     self.doc_len_dict = json.loads(f.read())
            self.doc_len_dict = weights["DocLen"]

        else:
            print("No pre-determined infos, generating new infos")
            self.docs = docs
            self.k1 = 1
            self.b = 0.75
            self.term_f_dict = defaultdict(lambda: dict())
            self.inverted_index = {}
            self.s = 0
            self.doc_len_dict = {}
            for index, doc in enumerate(self.docs):
                self.term_f_dict[str(index)] = Counter(doc)
                self.doc_len_dict[str(index)] = len(doc)
                self.s += len(doc)
                for token in doc:
                    if token in self.inverted_index:
                        if index not in self.inverted_index[token]:
                            self.inverted_index[token].append(index)
                    else:
                        self.inverted_index[token] = [index]

            self.doc_num = len(docs)
            self.avg_doc_num = self.s / self.doc_num

            weights = {"AvgDocNum": self.avg_doc_num, "DocNum": self.doc_num, "K1": self.k1, "B": self.b,
                       "TermFrequency": self.term_f_dict, "InvertedIndex": self.inverted_index, "DocLen":self.doc_len_dict, "FileNameList":file_name_list}

            print("saving new infos")
            with open("w.txt", "w") as f:
                f.write(json.dumps(weights))


    # Calculating BM25 for each word
    def single_score(self, word, docId):
        index = docId
        len_doc = self.doc_len_dict[str(index)]
        term_frequency = self.term_f_dict[str(index)]
        if word in term_frequency.keys():  # Frequency of the term appears in the document
            f = term_frequency[word] + 0.0
        else:
            f = 0.0
        n = len(self.inverted_index[word])
        # Calculate similarity, according to the formula
        s_score = ((f * (self.k1 + 1)) / (
                f + self.k1 * (1 - self.b + self.b * len_doc / self.avg_doc_num))) * math.log2(
            (self.doc_num - n + 0.5) / (n + 0.5))

        return s_score

    # Calculating BM25 score for given queries, but the result is not sorted
    def BM25_score(self, queries):
        doc_score_dict = {}
        for word in queries:
            if word in self.inverted_index.keys():
                docs = self.inverted_index[word]
                for idx in docs:
                    if str(idx) not in doc_score_dict:
                        doc_score_dict[str(idx)] = self.single_score(word, idx)
                    else:
                        score = doc_score_dict[str(idx)] + self.single_score(word, idx)
                        doc_score_dict[str(idx)] = score
        return doc_score_dict


# Automatically reads queries and generate results.
def automatic_query():
    start_time = datetime.datetime.now()
    with open("./files/queries.txt", 'r', encoding='utf-8') as f:
        content = f.read()
        queries = content.split("\n")

        i = 1  # query id
        lines = ""
        # preprocess queries
        for qs in queries:
            q_name = qs.split(" ")[0]
            qrs = clean_document(qs)
            qrs_list = clean_document(qrs).strip().split(" ")
            new_qrs_list = []
            for word in qrs_list:
                if word in stopwords:
                    continue
                word = poster_stemmer.stem(word)
                new_qrs_list.append(word)

            # get score for each query
            scores = bm.BM25_score(new_qrs_list)

            # rank the scores using sort

            ranked_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            j = 1

            # get top 15 ranks
            for docID, score in ranked_scores:
                if j <= 15:
                    # 1 1311 31 0.4481
                    # Query ID, Document ID, Rank, Similarity Score.
                    line = "{} {} {} {} \n".format(q_name, str(file_name_list[int(docID)]), j,
                                                   str(score))
                    j += 1
                    lines += line
                else:
                    break

            with open("./results.txt", "w") as f:
                f.write(lines)
            i += 1
    end_time = datetime.datetime.now()
    # Calculate running time for reference
    print(f"Query time:{int(end_time.timestamp() * 1000 - start_time.timestamp() * 1000)}ms")
    print(f"The automatic search is finished, please check the results in results.txt")

# Take user input as query and print result.
def manual_query():
    global start_time
    queries = input("Enter query:")
    while queries != "QUIT":
        if queries:
            start_time = datetime.datetime.now()
            try:
                # preprocess queries
                qrs = clean_document(queries)
                qrs_list = clean_document(qrs).strip().split(" ")
                new_qrs_list = []
                for word in qrs_list:
                    if word in stopwords:
                        continue
                    word = poster_stemmer.stem(word)
                    new_qrs_list.append(word)
                # get score for each query
                # rank the scores using sort
                scores = bm.BM25_score(new_qrs_list)
                ranked_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                i = 1
                lines = ""
                for docID, score in ranked_scores:
                    # get top 15 ranks
                    if i <= 15:
                        # 1 1311 31 0.4481
                        line = "{} {} {}\n".format(i, str(file_name_list[int(docID)]),
                                                   str(score))
                        i += 1
                        lines += line
                    else:
                        break
                print("\n")
                print("Results for query: [" + queries + "]")
                print(lines)

            except:
                print("Please re-enter the query")
                pass

        end_time = datetime.datetime.now()
        # Calculate running time for reference
        print(f"Query time:{int(end_time.timestamp() * 1000 - start_time.timestamp() * 1000)}ms")
        queries = input("\nEnter query:")


# Get file name list for docIDs (:list index)
def get_file_name_list(file_name):
    file_name_list = []
    with open(file_name, 'r', encoding='utf-8') as f:
        data = f.readlines()
    data = [item.strip() for item in data]
    for item in data:
        file_name_list.append(item)
    return file_name_list


# Get document list from index, provided just in case
def get_docs(file_name):
    doc_list = []
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    for item in lines:
        doc_list.append(item.split(" "))

    return doc_list


# load pre-saved files if exists, or generate new files with info.
def load_files():
    doc_list = []
    weights = {}
    # The program is not run for the first time
    if os.path.exists("w.txt"):
        print("Loading file name list, please wait.\n")
        with open("w.txt", 'r') as f:
            weights = json.loads(f.read())
            file_name_list = weights["FileNameList"]

    else:  # If the program is running for the first time,
        print("The program is running for the first time, please wait for intial generations.\n")
        print("Cleaning raw text. Creating file name list.")
        doc_list, file_name_list = raw_texts_cleaning("./documents/")
        print("Text tokenization")
        doc_list = text_tokenization(doc_list)

    return doc_list, file_name_list, weights


if __name__ == "__main__":
    # python search_small_corpus.py -m interactive
    try:
        if sys.argv[2] == "interactive":
            # Reading stopwords
            stopwords = set()
            with open("./files/stopwords.txt", 'r') as f:
                for line in f:
                    stopwords.add(line.rstrip())

            # Loading the porter stemmer
            poster_stemmer = PorterStemmer()

            # Text Preprocessing
            doc_list, file_name_list, weights = load_files()

            # Loading BM25 Model
            bm = BM25(doc_list, weights, file_name_list)

            manual_query()
        elif sys.argv[2] == "automatic":
            # Reading stopwords
            stopwords = set()
            with open("./files/stopwords.txt", 'r') as f:
                for line in f:
                    stopwords.add(line.rstrip())

            # Loading the porter stemmer
            poster_stemmer = PorterStemmer()

            # Text Preprocessing
            doc_list, file_name_list, weights = load_files()

            # Loading BM25 Model
            bm = BM25(doc_list, weights,file_name_list)

            automatic_query()
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} {sys.argv[1]} <mode from[interactive/automatic]>")