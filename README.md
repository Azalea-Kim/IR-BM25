# <center> COMP3009J 
# <center>Information Retrieval Programming Assignment
### <center> 
###This program can work for both the large and small corpus.

## 1. Overview
This program a ranked Information Retrieval(IR) system based on BM25 model.
- **Files submitted:**
  - **search_small_corpus.py**: the python file used for searching small corpus.
  - **search_large_corpus.py**: the python file used for searching big corpus.
  - **evaluate_small_corpus.py**: the python file used for evaluating small corpus.
  - **evaluate_large_corpus.py**: the python file used for evaluating big corpus.
  - **README.md**: Description and usage documentation for IR assignment.
  

- **Efficiency**
    - Efficient data structures and methods are used for faster processing times. 
    
    - The documents are pre-processed and weights/infos are gained in only one loop/nested-loop when indexing the corpus, to be cleaned, removed stopwords, stemmed, tokenized and indexed.
    During this process, dictionaries of inverted index, length of each docs, term frequency; weights like average doc length, doc length, k, b1; file name list whose index is the docID are generated and stored.
    And when this program is used starting for the second time, the pre-generated weights, infos and index can be loaded from the file and used, reducing the time cost.
    - Except for loops in queries, another loop of documents occurs in calculating BM25 score for each query. Since the score is separately calculated for a single query word within a particular doc. Since the word will not possibly appear in every document, so only the documents stored in inverted index of this word is looped, minimizing the search time.
    - In terms of the text cleaning, including normalization, several methods(sets, regex, translate, replace) where compared based on their time cost. (The use of set is to join the strings if it is not included in the set to be removed). As a result, translate ranked 1 and regex ranked 2. However, translate only allow "1-to-1 mapping from a single character string to its translation" so it cannot perform
 a " +" to " ". So for most processing, str.translate is used and for other replacement, regex expressions is used only for that situation mentioned. After replacing regex with translation:
      2000ms to 1700ms for small corpus indexing, 580000ms to 510000ms for the large corpus.
    
  - **Interactive Query Time**:      Fast, about 0ms-40ms for both the small and large corpus.
  - **Automatic Query Time**:       Fast, around 1100ms for small corpus and 2300ms for large corpus.
  - **Creating weights and info time**:         Around 1700ms for small corpus and 510000ms for large corpus.
  - **Loading weights and info time**:      Fast, around 40ms for small corpus and 4000ms for large corpus.
  - **Evaluation Time**:        Fast, around 0.00992s for both.

- **Discussion in raw text cleaning**
    - Originally, regex expressions as follows are used. These significantly affects the time efficiency negatively while seem to improve the precision. However, after removal of these operations, it had no negative impact to
the result and it improved Recall by 0.002; R-precision by 0.001; P@10 by 0.001; bpref by 0.02 in the small corpus and Precision by 0.001; R-precision by 0.009; bpref by 0.007 for the large corpus. 
So I decided to forbid the use of the operations mentioned as below.
  ```DOS
  s = re.sub(r"\'s", " ", s)
  s = re.sub(r"won't", "will not", s)
  s = re.sub(r"can\'t", "can not", s)
  s = re.sub(r"n\'t", " not", s)
  s = re.sub(r"\'re", " are", s)
  s = re.sub(r"\'d", " would", s)
  s = re.sub(r"\'ll", " will", s)
  s = re.sub(r"\'t", " not", s)
  s = re.sub(r"\'ve", " have", s)
  s = re.sub(r"\'m", " am", s)
  
    ```



    

## 2. User Instructions 
- This section includes two functionalities, **Query Search** and **Result Evaluation**. 
- .py files are separately provided for each of the large and small corpus files.
- The program will be run in the same directory as the README.md file in each corpus dataset file.
- Author's running environment: Python 3.8, mac os big sur 11.1.
- Please note that all files and folders should be placed in the correct directory and position. 

### 2.1 Query based on the BM25 model
**This program allows user to enter a query and then retrieve a list of the 15 most
relevant documents, according to the BM25 IR Model, sorted beginning with the highest
similarity score. And also allows user to perform automatic search of a formatted txt of queries, and generate top 15 results into a text file**
- **How to run it**
  
  Under the project directory, enter the following command on the command line.

    - For small corpus,
      ```DOS
      cd comp3009j-corpus-small
      
      python search_small_corpus.py -m interactive
      
      python search_small_corpus.py -m automatic
      ```
    - For large corpus,
      ```DOS
      cd comp3009j-corpus-large
      
      python search_large_corpus.py -m interactive
      
      python search_large_corpus.py -m automatic
      ```
    - When invalid input,
  ```DOS
  python search_large_corpus.py -m
  ```
  The output on the terminal will show instructions.
  ```DOS
  Usage: search_large_corpus.py -m <mode from[interactive/automatic]>
  ```
     


When the project is running for the first time, the system will display the following message and generate a **"weights.txt"** in the folder: 
```DOS
The program is running for the first time, please wait for initial generations.

Cleaning raw text. Creating weights and infos.
saving new infos
Creating weights time:1957ms

Initializing BM25 Model with given weight

```


**"weights.txt"** stores weights in a dictionary: 

*"AvgDocNum"* that stores average doc length 

*"DocNum"* that stores doc length 

*"K1"* that stores average k1
 
*"B"* that stores average b 

*"InvertedIndex"* that stores inverted index in form 
{"design": [0, 1, 3, 24, 34, ..],..} the lists includes the docIDs

*"FileNameList"* that stores the filename lists, the index is based on docIDs

*"DocLen"* that stores lengths of each doc

*"TermFrequency"* that stores term frequency in forms 
{"0": {"design": 1, "test": 1,..}, the key is the docID and the value of inner dic is the term frequency in this doc.

    
When the project is not running for the first time, the system will display the following message and load the weights from **"weights.txt"**.
  ```DOS
Loading BM25 weights and infos, please wait.

Loading weights time:38ms

Initializing BM25 Model with given weight

  ```  

  Following describes the "interactive" mode, where a user can manually type in queries and see the first 15 results 
in their command line, sorted beginning with the highest similarity score. The output should 
have three columns: the rank, the document’s ID, and the similarity score.
```DOS
Enter query:
```

  - **Output**
   
    After entering the query, the system will return a list of the 15 most relevant documents, according to the BM25 IR Model, sorted beginning with the highest
  similarity score. 
    - The sample output of small corpus is as follows.
    ```
        Loading BM25 weights and infos, please wait.
        
        Loading weights time:41ms
        
        Initializing BM25 Model with given weight
        Enter query:library information conference
        
        
        Results for query: [library information conference]
        1 251 7.476204110022498
        2 440 7.285834103174074
        3 1214 7.239895877157985
        4 1027 7.216921190472841
        5 36 6.829349609681709
        6 1334 6.650765985283065
        7 906 6.49932732171963
        8 882 6.462628198622034
        9 925 6.39045942013142
        10 41 6.183310583111942
        11 907 6.06887465664867
        12 265 6.020675442964211
        13 1042 5.957991944097192
        14 422 5.580347895214887
        15 866 5.580347895214887
        
        Query time:1ms
        
        Enter query:
    ```

    - The sample output of big corpus is as follows.
    ```
        Loading file name list, please wait.
    
        loading weights
        loading term frequency
        loading inverted index
        loading doc length
    
        Enter query:library information conference
        Results for query: [library information conference]
        1 GX233-05-9583623 6.927227758148971
        2 GX245-40-13733752 6.839048293916441
        3 GX243-53-8568136 6.725166179094919
        4 GX235-23-7414037 6.717495949821748
        5 GX002-25-16557885 6.672907219565086
        6 GX237-95-12105331 6.6253413767891605
        7 GX008-71-9359930 6.4522534951636565
        8 GX161-40-14898113 6.29166476187047
        9 GX022-73-15765418 6.250793836744613
        10 GX004-45-13410718 6.234580920027003
        11 GX243-66-2097962 6.148226771714304
        12 GX056-72-0417091 6.015110368734976
        13 GX238-44-5163478 5.982931267804389
        14 GX026-53-3204346 5.731499550684719
        15 GX234-46-1042559 5.705200992539126
        
        Query time:38ms
        
        Enter query:

    ```
    Then user can continue to type queries until exit.


- **Exit query**
  ```DOS
  Enter query:QUIT
  ```
  
Following describes the "automatic" mode, where the standard queries should be read from the 
*"queries.txt"* in the files directory. This file has a query on each line, beginning 
with its query ID in form (701  describe history oil industry). The results will pick the top 15 in one query and should be printed into a file named *“results.txt”*, which 
should include four columns: query ID, document ID, rank and similarity score.

  - **Output**
    - The sample output of small corpus is as follows.
    ```
    Loading BM25 weights and infos, please wait.

    Loading weights time:41ms

    Initializing BM25 Model with given weight
    Query time:1153ms
    
    The automatic search is finished, please check the results in results.txt

    ```
    - The result.txt of small corpus is as follows. The generation time is around 1000ms.
    ```
      1 51 1 28.348181822534364 
      1 486 2 25.5589643044615 
      1 12 3 22.41018236939531 
      1 878 4 22.35177312757023 
      1 573 5 19.010015608082703 
      1 944 6 17.23299654554877 
      1 746 7 16.9965354860423 
      1 141 8 16.11504101115914 
    ```

    - The result.txt of big corpus is as follows.(The Query time is around 2400ms.)
    ```
    701 GX232-43-0102505 1 9.138975937467617 
    701 GX255-56-12408598 2 8.74620818067563 
    701 GX229-87-1373283 3 8.689244510358648 
    701 GX253-41-3663663 4 8.613567490509304 
    701 GX064-43-9736582 5 8.58267974577204 
    701 GX268-35-11839875 6 8.565521983024242 
    701 GX231-53-10990040 7 8.470299369287467 

    ```
    


### 2.2 Evaluation
**The program can evaluate the effectiveness of the BM25 based IR model. The system will output scores based on the following evaluation metrics: Precision, Recall, P@10, R-precision, MAP, bpref.** 
- **How to run it** 

  Under the project directory, enter the following command on the command line.

  - For small corpus,
  ```DOS
  cd comp3009j-corpus-small
  
  python evaluate_small_corpus.py
  ```
  - For large corpus,
  ```DOS
  cd comp3009j-corpus-large
  
  python evaluate_large_corpus.py
  ```
  Then the results for each evaluation metrics will be printed on the terminal. 
  
- **Output**

  - Sample output of small corpus is as follows.
    ```
    
    Evaluation results:
    Precision:     0.229
    Recall:        0.486 
    R-precision:   0.378 
    P@10:          0.293 
    MAP:           0.361
    bpref:         0.486 
    
    Evaluation costs:0.009923999999999995s


    ```

  - Sample output of big corpus is as follows.
    ```
    
    Evaluation results:
    Precision:     0.535 
    Recall:        0.453
    R-precision:   0.376 
    P@10:          0.563
    MAP:           0.321
    bpref:         0.335 
    
    Evaluation costs:0.009704999999999998s

    
    ```


    
    


