# interactive -t 3:00:00 -m 250GB -a charlesgomez

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

## Read in Citing 
Citing_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv")
Citing_Dict = Citing_df.set_index("work_id")["citing_work_id"].to_dict()

## Extract Countries for Papers that Are Citing
Country_Citation_Dict = {x.split("+")[1]:x.split("+")[2] for k,v in  Citing_Dict.items() for x in v.split(" ") }
Year_Citation_Dict = {x.split("+")[1]:x.split("+")[0] for k,v in  Citing_Dict.items() for x in v.split(" ") }

## Combine Wikidata and Extracted Country_Dicts
Country_Dict = {**Country_Extracted_Terms_Dict, **Country_Wikidata_Dict}
Country_Dict = {**Country_Citation_Dict,**Country_Dict}

## Find the minimum year
Keywords_Dict_Filtered_Min_Year = {key:min([x.split("+")[0] for x in value]) for key, value in Keywords_Dict_Filtered.items()}

## For each minimum year, there may be multiple papers; we drop all terms with multiple papers in the same year. 
Keywords_Dict_Filtered_First_Paper = {key:[x.split("+")[1] for x in value if x.split("+")[0]==Keywords_Dict_Filtered_Min_Year[key]] for key, value in Keywords_Dict_Filtered.items()}
Keywords_Dict_Filtered_First_Paper = {key:value[0] for key, value in Keywords_Dict_Filtered_First_Paper.items() if len(value)==1} # The length of the list of min year papers should be 1 (or one paper)


## Return all citations made on the first paper with the term in Time_Window = 10 year time period.
Keywords_Dict_Filtered_Citing_Papers = {key:[x.split("+")[1] for x in return_Citations(value) if int(x.split("+")[0])<=(int(Keywords_Dict_Filtered_Min_Year[key])+Time_Window)] for key, value in Keywords_Dict_Filtered_First_Paper.items()}

## Repeat the above with the Wikidata
Wikidata_Dict_Filtered_Min_Year = {key:min([x.split("+")[0] for x in value]) for key, value in Wikidata_Dict_Filtered.items()}
Wikidata_Dict_Filtered_First_Paper = {key:[x.split("+")[1] for x in value if x.split("+")[0]==Wikidata_Dict_Filtered_Min_Year[key]] for key, value in Wikidata_Dict_Filtered.items()}
Wikidata_Dict_Filtered_First_Paper = {key:value[0] for key, value in Wikidata_Dict_Filtered_First_Paper.items() if len(value)==1}

## Return all citations made on the first paper with the Wikidata term in Time_Window = 10 year time period.
Wikidata_Dict_Filtered_Citing_Papers= {key:[x.split("+")[1] for x in return_Citations(value) if int(x.split("+")[0])<=(int(Wikidata_Dict_Filtered_Min_Year[key])+Time_Window)] for key, value in Wikidata_Dict_Filtered_First_Paper.items()}

## Papers that incorporate the term
Keywords_Dict_Filtered_Diffused_Papers = {key:[x.split("+")[1] for x in value if x.split("+")[0]>Keywords_Dict_Filtered_Min_Year[key]] for key, value in Keywords_Dict_Filtered.items()}
Wikidata_Dict_Filtered_Diffused_Papers = {key:[x.split("+")[1] for x in value if x.split("+")[0]>Wikidata_Dict_Filtered_Min_Year[key]] for key, value in Wikidata_Dict_Filtered.items()}

## Return all papers with the first term that were published in Time_Window = 10 year time period. 
Keywords_Dict_Filtered_Diffused_Papers = {key:[workid for workid in value if Year_Extracted_Terms_Dict[key][workid] <= (min(Year_Extracted_Terms_Dict[key].values())+Time_Window)] for key, value in Keywords_Dict_Filtered_Diffused_Papers.items()}

Wikidata_Dict_Filtered_Diffused_Papers = {key:[workid for workid in value if Year_Extracted_Wikidata_Terms_Dict[key][workid] <= (min(Year_Extracted_Wikidata_Terms_Dict[key].values())+Time_Window)] for key, value in Wikidata_Dict_Filtered_Diffused_Papers.items()}

## Combining Diffused and Citation Lists for both Keywords and Wikidata
Combined_Diffused_Papers = {key:Keywords_Dict_Filtered_Diffused_Papers.get(key,[])+Wikidata_Dict_Filtered_Diffused_Papers.get(key,[]) for key in set(list(Keywords_Dict_Filtered_Diffused_Papers.keys())+list(Wikidata_Dict_Filtered_Diffused_Papers.keys()))}


#################### Combination of Subset Terms and Removals

# Find all terms
list_of_terms = list(Combined_Diffused_Papers.keys())
list_of_terms.sort()

# First Round of Combination and Removal | Order the list of terms alphabetically
# Test if each adjacent pair of terms are subsets of one another AND if they have at least one paper in common
# How this is done: Remove non-alphanumeric characters, replace with white space and then split terms by white space into a list to see if lists overlap. 
# Add the term to the terms_to_remove list to remove in the main diffusion list. 
# Create a new dict that has this compound term (a,b) and its combined list. 
terms_to_remove = []
Common_Diffused_Round_1 = {}
for a, b in zip(list_of_terms, list_of_terms[1:]):
    if len(set(a.replace("/[\W_]+/g"," ").split(" ")) & set(b.replace("/[\W_]+/g"," ").split(" "))) > 0 and len(set(Combined_Diffused_Papers[a])&set(Combined_Diffused_Papers[b]))>0:
        try: 
            Common_Diffused_Round_1[(a,b)] = list(set(Combined_Diffused_Papers[a])|set(Combined_Diffused_Papers[b]))

            # delete 
            terms_to_remove.append(a)
            terms_to_remove.append(b)

        except:
            continue

# Second Part of Combination and Removal | Check compound terms in subsequent rounds of compounding until no more compounding terms are found. 
# Create two sets of dictionaries: Previous and Current
# Previous is the "previous round" of combinations (e.g., two terms), current would be the next round (e.g., three terms)
# Keep going until no more n-grams are found. 
Break_Check = True # Stop if no more compounding terms found
Combined_Common_Diffused_Terms = [] # List of dictionaries of dictionaries of compound terms to work ids in each round 
Common_Diffused_Round_Previous = Common_Diffused_Round_1 # set the Prevous and Current dictionaries
Combined_Common_Diffused_Terms.append(Common_Diffused_Round_Previous) #set the first set of two-terms as the first element in the combined list. 

while Break_Check==True:
    combined_terms_to_remove = [] # List of compound terms to remove in previous round dictionary
    Common_Diffused_Round_Current = {}
    for x, y in zip(list(Common_Diffused_Round_Previous.keys()), list(Common_Diffused_Round_Previous.keys())[1:]):
        if (tuple_check(x,y)) & (len(set(Common_Diffused_Round_Previous[x])&set(Common_Diffused_Round_Previous[y]))>0):
            try:
                Common_Diffused_Round_Current[tuple(set((x+y)))] = list(set(Common_Diffused_Round_Previous[x])|set(Common_Diffused_Round_Previous[y]))

                combined_terms_to_remove.append(x)
                combined_terms_to_remove.append(y) 

            except:
                continue

    for removal_ in combined_terms_to_remove:
        try:
            del Common_Diffused_Round_Previous[removal_]
        except:
            continue

    if len(Common_Diffused_Round_Current)>0:
        Combined_Common_Diffused_Terms.append(Common_Diffused_Round_Current)
        Common_Diffused_Round_Previous = Common_Diffused_Round_Current

    else: 
        Break_Check = False 


Combined_Common_Diffused_Terms = {k: v for d in Combined_Common_Diffused_Terms for k, v in d.items()}

######
## Need to Update 2024 04 07

dict_of_terms_reversed = {" ".join(key.split(" ")[::-1]).strip():key for key in list_of_terms}
list_of_terms_reversed = list(dict_of_terms_reversed.keys())
list_of_terms_reversed.sort()

Reversed_Common_Diffused_Round_1 = {}
for a, b in zip(list_of_terms_reversed, list_of_terms_reversed[1:]):
    if len(set(a.replace("/[\W_]+/g"," ").split(" ")) & set(b.replace("/[\W_]+/g"," ").split(" "))) > 0 and len(set(Combined_Diffused_Papers[dict_of_terms_reversed[a]])&set(Combined_Diffused_Papers[dict_of_terms_reversed[b]]))>0 & (tuple(set((dict_of_terms_reversed[a],dict_of_terms_reversed[b]))) not in list(Combined_Common_Diffused_Terms.keys())):

        try: 
            Reversed_Common_Diffused_Round_1[tuple(set((dict_of_terms_reversed[a],dict_of_terms_reversed[b])))] = list(set(Combined_Diffused_Papers[dict_of_terms_reversed[a]])|set(Combined_Diffused_Papers[dict_of_terms_reversed[b]]))

            # Delete 
            terms_to_remove.append(dict_of_terms_reversed[a])
            terms_to_remove.append(dict_of_terms_reversed[b])
        
        except:
            continue


# Second Part of Combination and Removal for Reversal Check | Check compound terms in subsequent rounds of compounding until no more compounding terms are found for reversed terms. 
# Create two sets of dictionaries just like before but now for reversals: Previous and Current
# Previous is the "previous round" of combinations (e.g., two terms), current would be the next round (e.g., three terms)
# Keep going until no more reversed n-grams are found. 
Break_Check = True # Stop if no more compounding terms found
Combined_Reversed_Common_Diffused_Terms = [] # List of dictionaries of dictionaries of compound terms to work ids in each round 
Reversed_Common_Diffused_Round_Previous = Reversed_Common_Diffused_Round_1 # set the Prevous and Current dictionaries reversed. 
Combined_Reversed_Common_Diffused_Terms.append(Reversed_Common_Diffused_Round_1) #set the first set of two-terms as the first element in the reversed combined list. 


while Break_Check==True:
    reversed_combined_terms_to_remove = [] # List of compound terms to remove in previous round dictionary
    Reversed_Common_Diffused_Round_Current = {}
    for x, y in zip(list(Reversed_Common_Diffused_Round_Previous.keys()), list(Reversed_Common_Diffused_Round_Previous.keys())[1:]):
        if (tuple_check(x,y)) & (len(set(Reversed_Common_Diffused_Round_Previous[x])&set(Reversed_Common_Diffused_Round_Previous[y]))>0) & (tuple(set((x+y))) not in list(Combined_Common_Diffused_Terms.keys())):
            try:
                Reversed_Common_Diffused_Round_Current[tuple(set((x+y)))] = list(set(Reversed_Common_Diffused_Round_Previous[x])|set(Reversed_Common_Diffused_Round_Previous[y]))

                reversed_combined_terms_to_remove.append(x)
                reversed_combined_terms_to_remove.append(y) 

            except:
                continue

    for removal_ in reversed_combined_terms_to_remove:
        try:
            del Reversed_Common_Diffused_Round_Previous[removal_]
        except:
            continue

    if len(Reversed_Common_Diffused_Round_Current)>0:
        Combined_Reversed_Common_Diffused_Terms.append(Reversed_Common_Diffused_Round_Current)
        Reversed_Common_Diffused_Round_Previous = Reversed_Common_Diffused_Round_Current

    else: 
        Break_Check = False 

Combined_Reversed_Common_Diffused_Terms = {k: v for d in Combined_Reversed_Common_Diffused_Terms for k, v in d.items()}


################# 
terms_to_remove = list(set(terms_to_remove))

Combined_Diffused_Papers = {k: v for k, v in Combined_Diffused_Papers.items() if k not in terms_to_remove}

Combined_Diffused_Papers.update(Combined_Common_Diffused_Terms)
Combined_Diffused_Papers.update(Combined_Reversed_Common_Diffused_Terms)


####################


Min_Year_Extracted_Combined_Terms_Dict = {}
Origin_Combined_Diffused_Papers = {}
for k, v in Combined_Common_Diffused_Terms.items():
    min_year = 0
    min_work_id = ''
    for term_ in k:
        try:
            work_years = Year_Extracted_Terms_Dict[term_]
            min_year_test_ = min(work_years.values())
            if min_year < min_year_test_:
                min_year = min_year_test_
                min_work_id = {v:k for k, v in work_years.items()}[min_year_test_]
            else:
                continue 
        except:
            continue 
    Min_Year_Extracted_Combined_Terms_Dict[k] = min_year
    Origin_Combined_Diffused_Papers[k] = min_work_id

#####################

Combined_Citations_Papers = { key:Keywords_Dict_Filtered_Citing_Papers.get(key,[])+Wikidata_Dict_Filtered_Citing_Papers.get(key,[]) for key in set(list(Keywords_Dict_Filtered_Citing_Papers.keys())+list(Wikidata_Dict_Filtered_Citing_Papers.keys())) }

Combined_Terms_Citations_Papers = {x:combine_all_citation_lists(x) for x in (set(list(Combined_Reversed_Common_Diffused_Terms.keys())) | set(list(Combined_Common_Diffused_Terms.keys())))}

Combined_Citations_Papers = {k: v for k, v in Combined_Citations_Papers.items() if k not in terms_to_remove}

Combined_Citations_Papers.update(Combined_Terms_Citations_Papers)


###############
common_keys = Combined_Citations_Papers.keys() & Combined_Diffused_Papers.keys()

Citing_Papers = {key:value for key, value in Combined_Citations_Papers.items() if key in common_keys and value!=[]}
Diffused_Papers = {key:value for key, value in Combined_Diffused_Papers.items() if key in common_keys and value!=[]}

common_keys = Citing_Papers.keys() & Diffused_Papers.keys()

Citing_Papers = {key:list(set(value)) for key, value in Citing_Papers.items() if key in common_keys and value!=[]}
Diffused_Papers = {key:list(set(value)) for key, value in Diffused_Papers.items() if key in common_keys and value!=[]}


## Minimum Year
Origin_Year_Diffused_Papers = Keywords_Dict_Filtered_Min_Year
Origin_Year_Diffused_Papers.update(Wikidata_Dict_Filtered_Min_Year)
Origin_Year_Diffused_Papers.update(Min_Year_Extracted_Combined_Terms_Dict)

Origin_Year_Diffused_Papers_df = pd.DataFrame(Origin_Year_Diffused_Papers.items(),columns=["Terms","Origin_Year"])

## Origin Diffused Papers
Origin_Diffused_Papers = Keywords_Dict_Filtered_First_Paper
Origin_Diffused_Papers.update(Wikidata_Dict_Filtered_First_Paper)
Origin_Diffused_Papers.update(Origin_Combined_Diffused_Papers)

Origin_Diffused_Papers_df = pd.DataFrame(Origin_Diffused_Papers.items(),columns=["Terms","Origin_Work_ID"])

## Number of Papers
Num_Citing_Papers_df = pd.DataFrame({k:len(list(set(v))) for k, v in Citing_Papers.items()}.items(), columns=["Terms","Number_of_Citing_Papers"])
Num_Diffused_Papers_df = pd.DataFrame({k:len(list(set(v))) for k, v in Diffused_Papers.items()}.items(), columns=["Terms","Number_of_Diffused_Papers"])

## Relate Keyword with Country of Origin
Country_Origin_Diffused_Papers = {key:return_Country(value) for key, value in Origin_Diffused_Papers.items()}
Country_Origin_Diffused_Papers = {key:Counter([y.split("-")[0] for y in value.split("=")]) for key, value in Country_Origin_Diffused_Papers.items() if value!='' and isinstance(value,float)==False}

Country_Origin_Diffused_Papers = {key:combine_values_in_counter_into_fractions(value) for key, value in Country_Origin_Diffused_Papers.items()}
Country_Origin_Diffused_Papers_df = pd.DataFrame(Country_Origin_Diffused_Papers).T.fillna(0).unstack().reset_index()
Country_Origin_Diffused_Papers_df = Country_Origin_Diffused_Papers_df.rename(columns={"level_0":"Country_of_Terms_Origin","level_1":"Terms",0:"Origin_Term_Weight"})
Country_Origin_Diffused_Papers_df = Country_Origin_Diffused_Papers_df.query("Origin_Term_Weight>0")

## Relate Keyword to All Diffused
Country_Diffused_Papers = {key:[return_Country(x) for x in value] for key, value in Diffused_Papers.items()}
#Country_Diffused_Papers = {key:[Counter([y.split("+")[0] for y in x[0].split(" ")]) for x in value if x!=''] for key, value in Country_Diffused_Papers.items()}
Country_Diffused_Papers = {key:[Counter([y.split("-")[0] for y in x.split("=")]) for x in value if x!='' and type (x) == str] for key, value in Country_Diffused_Papers.items()}
Country_Diffused_Papers = {key:[combine_values_in_counter_into_fractions(x) for x in value] for key, value in Country_Diffused_Papers.items()}
Country_Diffused_Papers = {key:merge_dicts(value) for key, value in Country_Diffused_Papers.items()}
Country_Diffused_Papers_df = pd.DataFrame(Country_Diffused_Papers).T.fillna(0).unstack().reset_index()
Country_Diffused_Papers_df = Country_Diffused_Papers_df.rename(columns={"level_0":"Country_of_Terms_Diffused","level_1":"Terms",0:"Term_Weight"})
Country_Diffused_Papers_df = Country_Diffused_Papers_df.query("Term_Weight>0")

## Relate Citations to All 
Country_Citing_Papers = {key:[return_Country(x) for x in list(set(value))] for key, value in Citing_Papers.items()}
#Country_Citing_Papers = {key:[Counter([y.split("-")[0] for y in x.split("=")]) for x in value if x!=''] for key, value in Country_Citing_Papers.items()}
# Fix 
#Country_Citing_Papers = {key:list(flatten(value)) for key, value in Country_Citing_Papers.items()}

#Country_Citing_Papers = {key:[Counter([re.split('\-|\+',y)[0]for y in re.split('=|\s+',x)]) for x in value if x!=''] for key, value in Country_Citing_Papers.items()}
Country_Citing_Papers = {key:[Counter([y.split("-")[0] for y in x.split("=")]) for x in value if x!='' and  pd.isna(x)==False] for key, value in Country_Citing_Papers.items()}

Country_Citing_Papers = {key:[combine_values_in_counter_into_fractions(x) for x in value] for key, value in Country_Citing_Papers.items()}
Country_Citing_Papers = {key:merge_dicts(value) for key, value in Country_Citing_Papers.items()}
Country_Citing_Papers_df = pd.DataFrame(Country_Citing_Papers).T.fillna(0).unstack().reset_index()
Country_Citing_Papers_df = Country_Citing_Papers_df.rename(columns={"level_0":"Country_of_Terms_Citing","level_1":"Terms",0:"Citing_Weight"})
Country_Citing_Papers_df = Country_Citing_Papers_df.query("Citing_Weight>0")

##
Country_Origin_Diffused_Papers_df = pd.merge(Country_Origin_Diffused_Papers_df,Origin_Year_Diffused_Papers_df,on=["Terms"])
Country_Diffused_Papers_df = pd.merge(Country_Diffused_Papers_df,Origin_Year_Diffused_Papers_df,on=["Terms"])
Country_Citing_Papers_df = pd.merge(Country_Citing_Papers_df,Origin_Year_Diffused_Papers_df,on=["Terms"])

##
Country_Diffused_Papers_df = pd.merge(Country_Diffused_Papers_df,Num_Diffused_Papers_df,on=["Terms"])
Country_Citing_Papers_df = pd.merge(Country_Citing_Papers_df,Num_Citing_Papers_df,on=["Terms"])

############################
### Index of Terms and Citations 
############################
cos_df = pd.DataFrame.from_dict({term_:returnCosine(list_,Diffused_Papers[term_]) for term_, list_ in Citing_Papers.items()},orient='index').reset_index().rename(columns={0:"Cosine","index":"Terms"})
overlap_df = pd.DataFrame.from_dict({term_:overlap_coefficient(set(list_),set(Diffused_Papers[term_])) for term_, list_ in Citing_Papers.items()},orient='index').reset_index().rename(columns={0:"SSOverlap","index":"Terms"})
js_df = pd.DataFrame.from_dict({term_:Jaccard_Similarity(list_,Diffused_Papers[term_]) for term_, list_ in Citing_Papers.items()},orient='index').reset_index().rename(columns={0:"Jaccard","index":"Terms"})

Similarity_Index_df = pd.merge(pd.merge(cos_df,overlap_df,on=["Terms"]),js_df,on=["Terms"])


############################
### Output 
############################
Country_Diffused_Papers_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_Diffused_Term_Edgelist_2024_03_19.csv",index=False)

Country_Citing_Papers_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_Citing_Term_Edgelist_2024_03_19.csv",index=False)

Country_Origin_Diffused_Papers_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_Origin_Term_Edgelist_2024_03_19.csv",index=False)

Similarity_Index_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_Similarity_Terms_and_Citations_2024_03_19.csv",index=False)

Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Input_Data/INPUT_Python_OpenAlex_Dictionary_Diffused_Citations_Origins_2024_03_19.pbz2"
with bz2.BZ2File(Filename_Dictionary, 'w') as f:
    cPickle.dump(Diffused_Papers, f, protocol=2)
    cPickle.dump(Citing_Papers,f, protocol=2)
    cPickle.dump(Origin_Diffused_Papers,f, protocol=2)
f.close()