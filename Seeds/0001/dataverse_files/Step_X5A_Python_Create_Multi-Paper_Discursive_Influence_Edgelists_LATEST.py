# interactive -t 3:00:00 -m 250GB -a charlesgomez
# interactive -t 3:00:00 -n 6 -m 70GB -a charlesgomez
# /home/u12/cjgomez/python38_latest.sif
###############################
### Modules
###############################
import os, io, sys
import os.path
from os import path
import pandas as pd 
import glob
import time
import re
import json
import numpy as np
import nltk
import string
from nltk.corpus import stopwords
from nltk import everygrams
import gc 
from nltk.stem import *
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer 
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.test.utils import common_corpus, common_dictionary #Note install gensim on Container
from gensim.corpora.dictionary import Dictionary
from collections import Counter
from pyathena import connect
import bz2 
import pickle
import _pickle as cPickle
import multiprocessing as mp
from dfply import *
import itertools

# Setting up pandarallel
#https://github.com/nalepae/pandarallel
#singularity run python38_202206.sif python3 -m pip install --user pandarallel
from pandarallel import pandarallel

from sklearn.metrics.pairwise import cosine_similarity

import math
from collections import Counter
from nltk import cluster


###############################
### Function
###############################

def combine_all_citation_lists(x):
    citation_list_ = []
    for item_ in x:
        try:
            citation_list_.extend(Combined_Citations_Papers[item_])
        except:
            continue
    return citation_list_

def tuple_check(x,y):
    for x_ in x:
        for y_ in y:
            if len(set(x_.replace("/[\W_]+/g"," ").split(" ")) & set(y_.replace("/[\W_]+/g"," ").split(" "))) > 0:
                return True 
            else:
                continue 
    return False

# def tuple_check(x,y):
#     for x1 in x:
#         for y1 in y:
#             if (x1 in y1)|(y1 in x1):
#                 return True 
#             else:
#                 continue 
#     return False  

def return_Citations(x):
    try:
        #return Citing_Dict[x.split("+")[1]].split(" ")
        return Citing_Dict[x].split(" ")
    except:
        return ''

def word2vec(word):
    from collections import Counter
    from math import sqrt

    # count the characters in word
    cw = Counter(word)
    # precomputes a set of the different characters
    sw = set(cw)
    # precomputes the "length" of the word vector
    lw = sqrt(sum(c*c for c in cw.values()))

    # return a tuple
    return cw, sw, lw

def cosdis(v1, v2):
    # which characters are common to the two words?
    common = v1[1].intersection(v2[1])
    # by definition of cosine distance we have
    return sum(v1[0][ch]*v2[0][ch] for ch in common)/v1[2]/v2[2]

def return_Country(x):
    try:
        return Country_Dict[x]
    except:
        return ''

def combine_values_in_counter_into_fractions(counter):
    new_counter = dict()
    for key, value in counter.items():
        new_counter[key] = value/sum(counter.values())
    return new_counter

def merge_dicts(dicts):
    merged_dict = {}
    for d in dicts:
        for k, v in d.items():
            if k in merged_dict:
                merged_dict[k] += v
            else:
                merged_dict[k] = v
    return merged_dict


def buildVector(iterable1, iterable2):
    counter1 = Counter(iterable1)
    counter2= Counter(iterable2)
    all_items = set(counter1.keys()).union( set(counter2.keys()) )
    vector1 = [counter1[k] for k in all_items]
    vector2 = [counter2[k] for k in all_items]
    return vector1, vector2

def returnCosine(l1,l2):
    v1,v2= buildVector(l1, l2)
    return 1 - cluster.util.cosine_distance(v1,v2)

def Jaccard_Similarity(set1,set2):
    set1 = set(set1)
    set2 = set(set2)
    C = set1.intersection(set2)
    D = set1.union(set2)
    return float(len(C))/float(len(D))

# Szymkiewicz–Simpson coefficient "Overlap Coefficient"
# https://medium.com/rapids-ai/similarity-in-graphs-jaccard-versus-the-overlap-coefficient-610e083b877d
def overlap_coefficient(set1, set2):
    """Computes the overlap coefficient between two sets.

    Args:
    set1: The first set.
    set2: The second set.

    Returns:
    The overlap coefficient.
    """

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / min(len(set1), len(set2))

############################
### Read in Keyword and Country Dictionaries 
############################

## Read in Citing 
#Citing_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv",low_memory=True)
Citing_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv")

#######
# chunk_size = 100000 #size of chunks relies on your available memory

# reader = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv",chunksize=chunk_size, low_memory=False)    

# for i, chunk in enumerate(reader):
#     out_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19_N{}.pkl".format(i+1)
#     with open(out_file, "wb") as f:
#         pickle.dump(chunk.set_index("work_id")["citing_work_id"].to_dict(),f,pickle.HIGHEST_PROTOCOL)
#     print(i+1)
#######

# import glob

# data_p_files=[]
# for name in glob.glob("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19_N*.pkl"):
#    data_p_files.append(name)

# Citing_List = []
# for file_name in data_p_files:
#     with open(file_name, 'rb') as input:
#         x = pickle.load(input)
#         Citing_List.append(x)



# Citing_df = pd.DataFrame([])
# for i in range(len(data_p_files)):
#     Citing_df = Citing_df.append(pd.read_pickle(data_p_files[i]),ignore_index=True)

########

Citing_Dict = Citing_df.set_index("work_id")["citing_work_id"].to_dict()


Time_Window = 10

Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Extracted_Terms_and_Wikidata_Dictionary_2024_03_19.pbz2"
f = bz2.BZ2File(Filename_Dictionary, 'rb')
Keywords_Dict_Filtered = cPickle.load(f)
Wikidata_Dict_Filtered = cPickle.load(f)
Country_Extracted_Terms_Dict = cPickle.load(f)

# Remove Year from Country_Dict for Extracted Terms
Country_Extracted_Terms_Dict = {key.split("+")[1]:value for key, value in Country_Extracted_Terms_Dict.items()}

# Extract Year from Keywords_Dict_Filtered for Extracted Terms
Year_Extracted_Terms_Dict = {key:{work.split("+")[1]:int(work.split("+")[0]) for work in value} for key, value in Keywords_Dict_Filtered.items()}

# Extract Year from Wikidata_Dict_Filtered for Extracted Terms
Year_Extracted_Wikidata_Terms_Dict = {key:{work.split("+")[1]:int(work.split("+")[0]) for work in value} for key, value in Wikidata_Dict_Filtered.items()}

## Read in Country for Wikidata
Country_Wikidata_Dict = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_2024_03_19.csv").set_index("work_id")["country"].to_dict()


## Extract Countries for Papers that Are Citing
Country_Citation_Dict = {x.split("+")[1]:x.split("+")[2] for k,v in  Citing_Dict.items() for x in v.split(" ") }
Year_Citation_Dict = {x.split("+")[1]:x.split("+")[0] for k,v in  Citing_Dict.items() for x in v.split(" ") }

## Combine Wikidata and Extracted Country_Dicts
Country_Dict = {**Country_Extracted_Terms_Dict, **Country_Wikidata_Dict}
Country_Dict = {**Country_Citation_Dict,**Country_Dict}


## Return all citations made on all papers 
Keywords_Dict_Filtered_Citing_Papers = {key:{x:return_Citations(x.split("+")[1]) for x in value} for key, value in Keywords_Dict_Filtered.items()}


## Discursive Influence ----------------------------------------------------------

# Step 1 | This lists out all terms and papers that include the term in their abstract or title
Diffusion_Dictionary = {key:[subkey for subkey, subvalue in value.items()] for key, value in Keywords_Dict_Filtered_Citing_Papers.items()}

def split_dict_equally(input_dict, chunks):
    "Splits dict by keys. Returns a list of dictionaries."
    # prep with empty dicts
    return_list = [dict() for idx in range(chunks)]
    idx = 0
    for k,v in input_dict.items():
        return_list[idx][k] = v
        if idx < chunks-1:  # indexes start at 0
            idx += 1
        else:
            idx = 0
    return return_list


def extract_Discursive_Influence(input_x,input_term):
    # input_x is the dictionary of all papers that use the term in its abstract of text
    # input_term is the term that is being used. 

    # Step 1 | Compare all papers with all other papers and check if they meet the criteria
    # paper1 is the original paper
    # paper2 is the future paper that is being compared; this is the one that uses the term from paper 1 potentially. 
    # paper 2 needs to be published after paper 1 but within the ten year time window
    paper_list = []
    for paper1, paper2 in itertools.permutations(input_x,2):
        if checkTime(paper1,paper2):
            paper_list.append([paper1,paper2])

    # Step 2 | Turn the list of lists into a DataFrame (Original - Paper 1) to then create a Dictionary, where the key is paper 1 (original paper)
    t2 = pd.DataFrame(paper_list).rename(columns={0:"Original",1:"Future"}).groupby("Original")["Future"].apply(list).to_dict()

    # Step 3 | For all candidate discursive influence papers (paper 2s), which ones also cite paper 1. 
    # NOTE 2024 04 23 | Need to collect list of citations that met this criterion so that we can 
    # go to attributional influence edgelists and REMOVE it. 
    t3 = {key:list(set(x.split("+")[1] for x in Keywords_Dict_Filtered_Citing_Papers[input_term][key])&set(x.split("+")[1] for x in value)) for key, value in t2.items()}

    # Step 4 | Remove all empty values. These are instances where no future papers that use the term in its abstract cite the focal original paper. 
    t3 = {key:value for key, value in t3.items() if value!=[]}

    return t3


def returnParallelDict(input_x):
    output_dict = {}
    for term, value in input_x.items():
        output_dict[term] = extract_Discursive_Influence(value,term)
    return output_dict

def checkTime(original,future):
    if int(future.split("+")[0])<=(int(original.split("+")[0])+Time_Window) and int(original.split("+")[0])<=(int(future.split("+")[0])) and original!=future:
        return True
    else:
        return False

import multiprocessing as mp
with mp.Pool(processes = 6) as p:
    results = p.map(returnParallelDict, split_dict_equally(Diffusion_Dictionary,6))

Discursive_Influence_Dictionary = dict(pair for d in results for pair in d.items())

# 2024 04 25 - Output Discursive Influence Dictionary to Attributional Influence Dictionary
# pickle(Discursive_Influence_Dictionary)
out_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_Discursive_Influence_Dictionary_2024_03_19.pkl"
with open(out_file, "wb") as f:
    pickle.dump(Discursive_Influence_Dictionary,f,pickle.HIGHEST_PROTOCOL)

Discursive_Influence_Dictionary_by_Country = {term:{paper1:[return_Country(y) for y in paper2] for paper1, paper2 in value.items()} for term, value in Discursive_Influence_Dictionary.items() }


Discursive_Influence_Dictionary_Number_of_Papers = {term:dict(Counter([x.split("+")[0] for x in list(value.keys())])) for term, value in Discursive_Influence_Dictionary.items() }

edgelist_ = []
for term_, value in Discursive_Influence_Dictionary_by_Country.items():
    #term_ = 'sapt'
    for x, y in value.items(): 
        year_ = x.split("+")[0]
        id_influenced_paper_ = x.split("+")[1]
        country_influencer_paper_ = return_Country(x.split("+")[1])
        influenced_papers_list_ = y
        edgelist_.extend([[term_,year_,id_influenced_paper_,country_influencer_paper_,i] for i in influenced_papers_list_])

Discursive_Influence_Dictionary_by_Country_df = pd.DataFrame(edgelist_).rename(columns={0:"Term",1:"Year",2:"Influencer_Paper_ID",3:"Influencer",4:"Influenced"})

def returnCountryCounter(x):
    if pd.isna(x)==False:
        counts_ = Counter(y.split("-")[0] for y in x.split("="))
        # FIX PERCENTAGES
        return {i:j/sum(counts_.values()) for i,j in counts_.items()}
    else:
        return Counter()

Discursive_Influence_Dictionary_by_Country_df["Influencer"] = Discursive_Influence_Dictionary_by_Country_df["Influencer"].apply(lambda x: returnCountryCounter(x))

Discursive_Influence_Dictionary_by_Country_df["Influenced"] = Discursive_Influence_Dictionary_by_Country_df["Influenced"].apply(lambda x: returnCountryCounter(x))


Influenced_m = pd.DataFrame([*Discursive_Influence_Dictionary_by_Country_df['Influenced']], Discursive_Influence_Dictionary_by_Country_df.index).stack()\
      .rename_axis([None,'Influenced']).reset_index(1, name='Influenced_Weights')

Influencer_m = pd.DataFrame([*Discursive_Influence_Dictionary_by_Country_df['Influencer']], Discursive_Influence_Dictionary_by_Country_df.index).stack()\
      .rename_axis([None,'Influencer']).reset_index(1, name='Influencer_Weights')

Discursive_Influence_Dictionary_by_Country_df = pd.merge(Discursive_Influence_Dictionary_by_Country_df[["Term","Year","Influencer_Paper_ID"]],
    Influenced_m,left_index=True,right_index=True)

Discursive_Influence_Dictionary_by_Country_df = pd.merge(Discursive_Influence_Dictionary_by_Country_df,
    Influencer_m,left_index=True,right_index=True)

Discursive_Influence_Dictionary_by_Country_df["Weight"] = Discursive_Influence_Dictionary_by_Country_df["Influencer_Weights"] * Discursive_Influence_Dictionary_by_Country_df["Influenced_Weights"]

Discursive_Influence_Dictionary_by_Country_df = Discursive_Influence_Dictionary_by_Country_df.groupby(["Term","Year","Influencer","Influenced"])["Weight"].sum().reset_index()

# With a ten-year time window, we stop at 2013.
Discursive_Influence_Dictionary_by_Country_df = Discursive_Influence_Dictionary_by_Country_df.query("Year<='2013'")

Discursive_Influence_Dictionary_Term_Year_Number_of_Papers_df = pd.DataFrame.from_dict(Discursive_Influence_Dictionary_Number_of_Papers,orient='index').unstack().reset_index().rename(columns={'level_0':"Year",'level_1':"Term",0:"Number_of_Papers_with_Term_and_Cite"}).query("Year<='2013'").groupby(["Term"]).sum("Term_Year_Number_of_Papers").reset_index()

Discursive_Influence_Dictionary_by_Country_df = pd.merge(Discursive_Influence_Dictionary_by_Country_df,Discursive_Influence_Dictionary_Term_Year_Number_of_Papers_df,on=["Term"])

## Update 204 04 25 ------
## Need to return a dictionary of origin paper keys to what is citing it & incorporates the term. 
## Upload dict to attributional influence to remove cites. 
# Keywords_Dict_Filtered_Citing_Papers = {key:{x:return_Citations(x.split("+")[1]) for x in value} for key, value in Keywords_Dict_Filtered.items()}



## Output
Discursive_Influence_Dictionary_by_Country_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv",index=False)
