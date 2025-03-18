import datetime
import json
import math
import os
import re
import string
import sys

from files.porter import PorterStemmer


#
# This is code for small corpus
#


# TEXT PRE-PROCESSING

def clean_document(s):
    # normalisation: lowercase, delete full stops U.S.A, delete hyphens
    # cleaning documents
    s = s.lower()

    # delete hyphens and punctuations and digits

    # translate is faster than regex. But only allows 1 from a single character string to 1
    table = str.maketrans(dict.fromkeys(string.punctuation))  # OR {key: None for key in string.punctuation}
    s = s.translate(table)
    table1 = str.maketrans(dict.fromkeys(string.digits))
    s = s.translate(table1)


    # delete white spaces
    s = re.sub(' +', ' ', s)
    dict_white = dict.fromkeys(string.whitespace)
    dict_white.pop(" ")
    table2 = str.maketrans(dict_white)
    s = s.translate(table2)

    return s.strip()


#  Extract the documents contained in the document collections provided.
#  This function converts documents into index and outputs a dict containing the index，
#  filename list and weights required by BM25
def corpus_indexing(docs_dir):
    file_name_list = []
    # Folder traversal
    file_count = 0
    inverted_index ={}
    doc_len_dict ={}
    all_doc_len = 0
    term_frequency ={}
    # Folder traversal
    for file_name in os.listdir(docs_dir):
        try:
            document_file_name = docs_dir + "/" + file_name
            # Open file in the folder
            with open(document_file_name, 'r', encoding='utf-8') as f:
                content = f.read()
                file_name_list.append(file_name)
                file_count += 1
                # Record the content of the document after cleaning
                content = clean_document(content).strip()
                "simple shear flow past a flat plate in an incompressible fluid of small viscosity. in "
                # Perform text_tokenization as well as stop word removal, and stemming
                terms = content.split(" ")

                doc_len_count =0
                index = file_count-1
                term_frequency[str(index)] = {}
                for word in terms:
                    # Do stop word removal and stemming
                    if word in stopwords:
                        continue

                    word = poster_stemmer.stem(word)
                    if word != "":
                        doc_len_count += 1
                        # create/update inverted index

                        if word in inverted_index:
                            if word not in inverted_index[word]:
                                if inverted_index[word][-1] != index:
                                    inverted_index[word].append(index)
                        else:
                           inverted_index[word] = [index]

                        # create/update term frequency dict
                        if word in term_frequency[str(index)]:
                            term_frequency[str(index)][word] += 1
                        else:
                            term_frequency[str(index)][word] = 1

                doc_len_dict[str(index)] = doc_len_count
                all_doc_len += doc_len_count

        except:
            pass


    avg_doc_num = all_doc_len / file_count


    weights = {"AvgDocNum": avg_doc_num, "DocNum": file_count, "K1": 1, "B": 0.75,"InvertedIndex": inverted_index,"DocLen": doc_len_dict,
               "TermFrequency":term_frequency,
               "FileNameList": file_name_list}

    # save weights and infos to file
    print("saving new infos")
    with open("weights.txt", "w") as f:
        f.write(json.dumps(weights))

    return weights


class BM25(object):
    def __init__(self, weights):
        # Initialize BM25 Model with given weight

        print("Initializing BM25 Model with given weight")
        self.doc_num = weights["DocNum"]
        self.avg_doc_num = weights["AvgDocNum"]
        self.k1 = weights["K1"]
        self.b = weights["B"]
        self.term_f_dict = weights["TermFrequency"]
        self.inverted_index = weights["InvertedIndex"]
        self.doc_len_dict = weights["DocLen"]

    # Calculating BM25 for each word
    def single_score(self, word, docId):
        index = docId
        len_doc = self.doc_len_dict[str(index)]
        term_frequency = self.term_f_dict[str(index)]
        if word in term_frequency.keys():
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
        # calculate on each word in queries
        for word in queries:
            if word in self.inverted_index.keys():
                # loop through the docs that this word exist
                docs = self.inverted_index[word]
                for idx in docs:
                    # add scores of one doc of this query
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
    print(f"Query time:{int(end_time.timestamp() * 1000 - start_time.timestamp() * 1000)}ms""\n")
    print(f"The automatic search is finished, please check the results in results.txt")

# Take user input as query and print result.
def manual_query():
    global start_time
    queries = input("Enter query:")
    # Ask user to enter new query until QUIT is typed
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



# load pre-saved files if exists, or generate new files with info.
def load_files():
    # The program is not running for the first time
    if os.path.exists("weights.txt"):
        # load weights
        start_time = datetime.datetime.now()
        print("Loading BM25 weights and infos, please wait.\n")
        with open("weights.txt", 'r') as f:
            weights = json.loads(f.read())

        end_time = datetime.datetime.now()
        # Calculate running time for reference
        print(f"Loading weights time:{int(end_time.timestamp() * 1000 - start_time.timestamp() * 1000)}ms""\n")


    else:  # If the program is running for the first time,
        start_time = datetime.datetime.now()
        print("The program is running for the first time, please wait for initial generations.\n")
        print("Cleaning raw text. Creating weights and infos.")

        # text-preprocess and tokenize
        # indexing tokens

        weights = corpus_indexing("./documents/")
        end_time = datetime.datetime.now()
        # Calculate running time for reference
        print(f"Creating weights time:{int(end_time.timestamp() * 1000 - start_time.timestamp() * 1000)}ms""\n")



    return weights

if __name__ == "__main__":

    try:
        # python search_small_corpus.py -m interactive
        if sys.argv[2] == "interactive":
            # Reading stopwords
            stopwords = set()
            with open("./files/stopwords.txt", 'r') as f:
                for line in f:
                    stopwords.add(line.rstrip())

            # Loading the porter stemmer
            poster_stemmer = PorterStemmer()

            # Text Preprocessing and indexing
            weights = load_files()
            file_name_list = weights["FileNameList"]

            # Loading BM25 Model
            bm = BM25(weights)

            manual_query()
        # python search_small_corpus.py -m automatc
        elif sys.argv[2] == "automatic":
            # Reading stopwords
            stopwords = set()
            with open("./files/stopwords.txt", 'r') as f:
                for line in f:
                    stopwords.add(line.rstrip())

            # Loading the porter stemmer
            poster_stemmer = PorterStemmer()

            # Text Preprocessing and indexing
            weights = load_files()
            file_name_list = weights["FileNameList"]

            # Loading BM25 Model
            bm = BM25(weights)

            automatic_query()
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} {sys.argv[1]} <mode from[interactive/automatic]>")