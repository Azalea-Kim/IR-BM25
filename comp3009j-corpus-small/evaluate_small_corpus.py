import time
from collections import defaultdict


# Read the qrels.txt and
# return the relevance analysis of documents {query_id: {docId: relevance_judgement}}
def get_qrels():
    qrels_dict = {}
    with open("./files/qrels.txt", 'r') as f:
        # 1 0 184 2  q,*,doc, rank
        line = f.readline()
        while line:
            line_content = line.split(" ")
            if line_content[0] in qrels_dict:
                (qrels_dict[line_content[0]])[line_content[2]] = line_content[3].strip()
            else:
                qrels_dict[line_content[0]] = {line_content[2]: line_content[3].strip()}
            line = f.readline()
    return qrels_dict


# Read the results.txt and
# return the content dict {query_id: [docId1, docId2,...]}
def get_results():
    result_dict = defaultdict(lambda: [])
    with open("./results.txt", 'r') as f:
        results = f.readlines()
        results = [item.strip().split(" ") for item in results]
        # There are no unjudged documents in small corpus, so all documents can be calculated as relevant
        for item in results:
            # query_id : file_id
            # 1 51 1 28.348181822534364  q, doc, rank, score
            result_dict[str(item[0])].append(item[1])
    return result_dict

# Precision
def get_precision():
    precision = 0
    for query_id in results_dict.keys():
        results = results_dict[query_id]
        ret= len(results)
        correct = 0
        for doc_id in qrels_dict[query_id].keys(): # relevance
            if doc_id in results:
                if qrels_dict[query_id][doc_id] != "0":
                    correct += 1
        p = correct/ret
        precision+=p

    return format(precision / len(results_dict.keys()), ".3f")


def get_recall():
    recall = 0
    for query_id in results_dict.keys():
        results = results_dict[query_id]
        rel= 0
        correct = 0
        for doc_id in qrels_dict[query_id].keys(): # relevance

            if qrels_dict[query_id][doc_id] != "0":

                    rel += 1
                    if doc_id in results:
                        correct +=1
        if rel == 0:
            continue
        r = correct/rel
        recall+=r

    return format(recall / len(results_dict.keys()), ".3f")

# p@10
def get_p10():
    p10 = 0
    for query_id in results_dict.keys():
        results = results_dict[query_id][:10]
        correct = 0
        for doc_id in qrels_dict[query_id].keys():  # relevance
            if doc_id in results:
                if qrels_dict[query_id][doc_id] != "0":
                    correct += 1
        p10 += correct/10

    return format(p10 / len(results_dict.keys()), ".3f")


# R-precision
def get_r_precision():
    rp = 0
    for query_id in results_dict.keys():
        rel= 0
        for doc_id in qrels_dict[query_id].keys(): # relevance
            if qrels_dict[query_id][doc_id] != "0":
                    rel += 1
        results = results_dict[query_id][:rel]
        correct = 0
        for doc_id in qrels_dict[query_id].keys():  # relevance
            if doc_id in results:
                if qrels_dict[query_id][doc_id] != "0":
                    correct += 1
        if rel == 0:
            continue
        rp += correct / rel
    return format(rp / len(results_dict.keys()), ".3f")


# Mean Average Precision (MAP)
def get_map():
    map = 0
    for query_id in results_dict.keys():
        results = results_dict[query_id]
        qrels = qrels_dict[query_id]
        ret = 1
        p = 0
        p_correct = 0
        while ret<=len(results):
            if results[ret-1] in qrels.keys():
                if qrels[results[ret-1]] != "0":
                    p_correct+=1
                    pp = p_correct/ret
                    p+=pp
            ret += 1
        if p_correct == 0:
            continue

        relevant_num = 0
        for value in qrels.values():
            if value != "0":
                relevant_num += 1
        a = p / relevant_num
        map += a

    return format(map / len(results_dict.keys()), ".3f")


def get_bpref():
    bpref = 0
    for query_id in results_dict.keys():
        results = results_dict[query_id]
        qrels = qrels_dict[query_id]
        relevant_num = 0
        for value in qrels.values():
            if value != "0":
                relevant_num += 1
        non_relevant_count = 0
        p = 0
        for result in results:
            if result in qrels.keys(): # not U
                if qrels[result] == "0": # N
                    non_relevant_count +=1
                else: #R
                    p += (1-non_relevant_count/relevant_num)
        bpref += p/relevant_num
    return format(bpref / len(results_dict.keys()), ".3f")




if __name__ == "__main__":
    start_time = time.process_time()


    results_dict = get_results()
    qrels_dict = get_qrels()

    print("Evaluation results:")
    print("{:<14} {:<4}".format("Precision:", get_precision()))
    print("{:<14} {:<4}".format("Recall:",get_recall()))
    print("{:<14} {:<4}".format("R-precision:",get_r_precision()))
    print("{:<14} {:<4}".format("P@10:",get_p10()))
    print("{:<14} {:<4}".format("MAP:",get_map()))
    print("{:<14} {:<4}".format("bpref:",get_bpref()))

    end_time = time.process_time()
    # Calculate running time for reference
    print(f"\nEvaluation costs:{end_time - start_time}s")


