# interactive -t 13:00:00 -n 20 -m 6GB -a charlesgomez

# interactive -t 3:00:00 -m 250GB -a charlesgomez
# interactive -t 3:00:00 -n 6 -m 50GB -a charlesgomez

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

def return_Citations(x):
    try:
        #return Citing_Dict[x.split("+")[1]].split(" ")
        return Citing_Dict[x].split(" ")
    except:
        return ''

def return_Citations_as_Generator(x):
    try:
        #return Citing_Dict[x.split("+")[1]].split(" ")
        return (Citing_Dict[x].split(" "))
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

Time_Window = 10

Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Extracted_Terms_and_Wikidata_Dictionary_2024_03_19.pbz2"
f = bz2.BZ2File(Filename_Dictionary, 'rb')
Keywords_Dict_Filtered = cPickle.load(f)
Wikidata_Dict_Filtered = cPickle.load(f)
Country_Extracted_Terms_Dict = cPickle.load(f)

print("Step 1 Complete")

## Prepare Extracted Terms ---------------------------------

# Remove Year from Country_Dict for Extracted Terms
Country_Extracted_Terms_Dict = {key.split("+")[1]:value for key, value in Country_Extracted_Terms_Dict.items()}

# Extract Year from Keywords_Dict_Filtered for Extracted Terms
Year_Extracted_Terms_Dict = {key:{work.split("+")[1]:int(work.split("+")[0]) for work in value} for key, value in Keywords_Dict_Filtered.items()}

# Extract Year from Wikidata_Dict_Filtered for Extracted Terms
Year_Extracted_Wikidata_Terms_Dict = {key:{work.split("+")[1]:int(work.split("+")[0]) for work in value} for key, value in Wikidata_Dict_Filtered.items()}

## Read in Country for Wikidata
Country_Wikidata_Dict = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_2024_03_19.csv").set_index("work_id")["country"].to_dict()

## Prepare Massive Citation DataFrame as a Dictionary ---------------------------------

## Read in Citing 
Citing_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv")
Citing_Dict = Citing_df.set_index("work_id")["citing_work_id"].to_dict()

print("Step 2 Complete")

## Create Dictionaries of Country to Citation Affiliation and Year Citations  ---------------------------------

## Extract Countries for Papers that Are Citing
Country_Citation_Dict = {x.split("+")[1]:x.split("+")[2] for k,v in  Citing_Dict.items() for x in v.split(" ") }
Year_Citation_Dict = {x.split("+")[1]:x.split("+")[0] for k,v in  Citing_Dict.items() for x in v.split(" ") }

## Combine Wikidata and Extracted Country_Dicts
Country_Dict = {**Country_Extracted_Terms_Dict, **Country_Wikidata_Dict}
Country_Dict = {**Country_Citation_Dict,**Country_Dict}

print("Step 3 Complete")

del Citing_df
gc.collect()

## Discursive Influence File ---------------------------------

disursive_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_Discursive_Influence_Dictionary_2024_03_19.pkl"
#f = bz2.BZ2File(disursive_file, 'rb')
with open(disursive_file, "rb") as input_file:
    Discursive_Influence_Dict = pickle.load(input_file)

## Create Empty Keyword to Citing Paper Dict -------------------------------------------
### N.B., Since memory issues abound, keep list of citations empty for now. 

Keywords_Dict_Filtered_Citing_Papers = {}
for key, value in Keywords_Dict_Filtered.items():
    keyword_list = {}
    for x in value:
        if return_Citations(x.split("+")[1])!='':
            keyword_list[x] = {}
    Keywords_Dict_Filtered_Citing_Papers[key] = keyword_list


## Attributional Influence Helper Functions ----------------------------------------------------------

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

def returnCountryCounter(x):
    if pd.isna(x)==False:
        counts_ = Counter(y.split("-")[0] for y in x.split("="))
        # FIX PERCENTAGES
        return {i:j/sum(counts_.values()) for i,j in counts_.items()}
    else:
        return Counter()


## Attributional Influence Main Parallel Function -------------------------------------------


def return_Attributional_Influence(input_dict):

    full_citing_list = []
    for term, value in input_dict.items():

        discursive_influence_list = list(Discursive_Influence_Dict[term].keys())

        for paper, citation_list in value.items(): 
            paper_year_ = paper.split("+")[0]

            # Update - 2024 05 02
            citation_list = list(set(return_Citations(paper.split("+")[1])))

            # Update - 2024 05 02
            # Filter out discursive influence cites
            citation_list = [cite_id for cite_id in citation_list if cite_id.split("+")[1] not in discursive_influence_list]

            if int(paper_year_) > 2013:
                continue 

            paper_id_ = paper.split("+")[1]
            if pd.isna(return_Country(paper_id_))==False:
                
                paper_country_ = dict(Counter([x.split("-")[0] for x in return_Country(paper_id_).split("=")]))
                paper_country_ = {x:y/sum(paper_country_.values()) for x, y in paper_country_.items()}
                
                citing_paper_country_ = [dict(Counter([y.split("-")[0] for y in x.split("+")[2].split("=")])) for x in citation_list if int(x.split("+")[0])<=(int(paper_year_)+Time_Window)]
                citing_paper_country_ = [{x1:x2/sum(x.values()) for x1, x2, in x.items()}for x in citing_paper_country_]

                full_citing_list.append([term,paper_id_,paper_year_,paper_country_,citing_paper_country_])

    return full_citing_list

print("Step 4 Complete")


## Create First Attributional Infuence DataFrame -------------------------------------------

## This lists out all terms and papers that include the term in their abstract or title
with mp.Pool(processes = 20) as p:
    results = p.map(return_Attributional_Influence, split_dict_equally(Keywords_Dict_Filtered_Citing_Papers,100)) #Originally 30 

print("Step 5 Complete")

Attributional_Influence_df = pd.concat([pd.DataFrame(x,columns=["Term","Influencer_Paper_ID","Year","Cited_Receiver","Citing_Sender"]) for x in results])

Attributional_Influence_df = Attributional_Influence_df.rename(columns={"Cited_Receiver":"Influencer","Citing_Sender":"Influenced"})

# Remove rows with no country information, i.e., []
Attributional_Influence_df = Attributional_Influence_df[Attributional_Influence_df['Influencer'].str.len()>0]
Attributional_Influence_df = Attributional_Influence_df[Attributional_Influence_df['Influenced'].str.len()>0]

Attributional_Influence_df = Attributional_Influence_df.reset_index(drop=True)

print("Step 6 Complete")

## Output Attributional DataFrame -------------------------------------------

out_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_Attributional_Influence_DataFrame_Dictionary_2024_03_19.pkl"
with open(out_file, "wb") as f:
    pickle.dump(Attributional_Influence_df,f,pickle.HIGHEST_PROTOCOL)

print("Step 7 Complete")

## Read in Attributional DataFrame -------------------------------------------

attributional_influence_dataframe_dict_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_Attributional_Influence_DataFrame_Dictionary_2024_03_19.pkl"
with open(attributional_influence_dataframe_dict_file, "rb") as input_file:
    Attributional_Influence_df = pickle.load(input_file)

print("Step 8 Complete")

## Create Attributional Count DataFrame -------------------------------------------
## Number of Citations Received per Influencer Paper-Year | Go through each low and return the length of the list / check if that's the number
Attributional_Influence_df_Count = pd.merge(Attributional_Influence_df[["Term","Year","Influencer_Paper_ID"]],Attributional_Influence_df["Influenced"].apply(lambda row_: sum([sum(x.values()) for x in row_])),left_index=True,right_index=True).rename(columns={"Influenced":"Number_of_Citations_per_Influencer_Paper"})

print("Step 9 Complete")

## Helper Code for Attributional County-to-Country DataFrame -------------------------------------------

def computeInfluenceWeight(input_row_):
    input_Influencer = input_row_["Influencer"]
    input_Influenced = input_row_["Influenced"]
    year_ = input_row_["Year"]
    term_ = input_row_["Term"]

    edgelist_ = []

    if type(input_Influencer)!=list:
        input_Influencer = [input_Influencer]

    if type(input_Influenced)!=list:
        input_Influenced = [input_Influenced]


    for x in input_Influencer:
        for y in input_Influenced:
            edgelist_.append([term_,year_,list(x.keys())[0],list(y.keys())[0],list(x.values())[0]*list(y.values())[0]])
    
    edgelist_ = pd.DataFrame(edgelist_,columns=["Term","Year","Influencer","Influenced","Influenced_Weights"]).groupby(["Term","Year","Influencer","Influenced"])["Influenced_Weights"].sum().reset_index()

    return edgelist_

def returnParallelInfluence(input_dataframe_):
    list_ = []
    print("Testing")
    for index, row_ in input_dataframe_.iterrows():
        list_.append(computeInfluenceWeight(row_))

    return pd.concat(list_) 

## Complete Attributional County-to-Country DataFrame -------------------------------------------


with mp.Pool(processes = 10) as p:
    results = p.map(returnParallelInfluence, np.array_split(Attributional_Influence_df, 100))

print("Step 9 Complete")

Attributional_Influence_df_Country = pd.concat(results)

Attributional_Influence_df_Country = Attributional_Influence_df_Country.groupby(["Influencer","Influenced","Year","Term"])["Influenced_Weights"].sum().reset_index()

## Output | Attributional  -------------------------------------------

Attributional_Influence_df_Country.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv",index=False)

Attributional_Influence_df_Count.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_Attributional_Influence_2024_03_19.csv",index=False)

##################
