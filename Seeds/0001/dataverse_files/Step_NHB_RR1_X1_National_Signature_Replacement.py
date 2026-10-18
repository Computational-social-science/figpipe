# PUMA
# interactive -t 3:00:00 -m 250GB -a charlesgomez
# interactive -t 3:00:00 -n 6 -m 70GB -a charlesgomez
# /home/u12/cjgomez/python38_latest.sif ipython

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

def returnCountryCounter(x):
    if pd.isna(x)==False:
        counts_ = Counter(y.split("-")[0] for y in x.split("="))
        # FIX PERCENTAGES
        return {i:j/sum(counts_.values()) for i,j in counts_.items()}
    else:
        return Counter()

############################
### *************************
### IMPORTANT - Start below and skip this section; start at self/alter edgelist input code line. 
### *************************
############################


############################
### Read in Keyword and Country Dictionaries 
############################

## Read in Citation Data ----------------------------------------------------------
Citing_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Citing_IDs_for_Extracted_and_WikiData_Terms_2024_03_19.csv")
Citing_Dict = Citing_df.set_index("work_id")["citing_work_id"].to_dict()

## Time Frame ----------------------------------------------------------

Time_Window = 10

## Read in Keyword Dictionaries ----------------------------------------------------------
Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Extracted_Terms_and_Wikidata_Dictionary_2024_03_19.pbz2"
f = bz2.BZ2File(Filename_Dictionary, 'rb')
Keywords_Dict_Filtered = cPickle.load(f)
Wikidata_Dict_Filtered = cPickle.load(f)
Country_Extracted_Terms_Dict = cPickle.load(f)

# Remove Year from Country_Dict for Extracted Terms
Country_Extracted_Terms_Dict = {key.split("+")[1]:value for key, value in Country_Extracted_Terms_Dict.items()}

## Read in Country for Wikidata
Country_Wikidata_Dict = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_2024_03_19.csv").set_index("work_id")["country"].to_dict()

## Extract Countries for Papers that Are Citing
Country_Citation_Dict = {x.split("+")[1]:x.split("+")[2] for k,v in  Citing_Dict.items() for x in v.split(" ") }

## Combine Wikidata and Extracted Country_Dicts
Country_Dict = {**Country_Extracted_Terms_Dict, **Country_Wikidata_Dict}
Country_Dict = {**Country_Citation_Dict,**Country_Dict}

############################
### Read in Discurisve Influence Dictionary 
############################
in_file = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_Discursive_Influence_Dictionary_2024_03_19.pkl"

with open(in_file, 'rb') as file:
	Discursive_Influence_Dictionary = pickle.load(file)

Discursive_Influence_Dictionary_by_Country = {term:{paper1:[return_Country(y) for y in paper2] for paper1, paper2 in value.items()} for term, value in Discursive_Influence_Dictionary.items() }

## Create Term Adoption by Country List ----------------------------------------------------------
## This creates a "national signature" of each country per year of terms found in titles/abstracts
## This is weighted by the full adoption of the term (1) or partial adoption of the paper is internationlly
## coauthored.
term_paper_adoption_list_ = []
for term_, value in Discursive_Influence_Dictionary_by_Country.items():
    #term_ = 'sapt'
    for x, y in value.items(): 
        year_ = x.split("+")[0]
        id_influenced_paper_ = x.split("+")[1]
        influenced_papers_list_ = y
        term_paper_adoption_list_.extend([[term_,year_,id_influenced_paper_,i] for i in influenced_papers_list_])

## Only focus on the "influenced" paper, the paper that uses the term.
Term_Adoption_by_Country_df = pd.DataFrame(term_paper_adoption_list_).rename(columns={0:"Term",1:"Year",2:"Influenced_Paper_ID",3:"Influenced_Country"})

Term_Adoption_by_Country_df = Term_Adoption_by_Country_df.drop_duplicates()

Term_Adoption_by_Country_df['Influenced_Country_Percent'] = Term_Adoption_by_Country_df['Influenced_Country'].apply(lambda x: returnCountryCounter(x))

del Term_Adoption_by_Country_df['Influenced_Country']

m = pd.DataFrame([*Term_Adoption_by_Country_df['Influenced_Country_Percent']], Term_Adoption_by_Country_df.index).stack()\
      .rename_axis([None,'Country']).reset_index(1, name='Percent_Weight')

Term_Adoption_by_Country_df = Term_Adoption_by_Country_df[['Term','Year','Influenced_Paper_ID']].join(m)

## Read in Censored Terms (10K) ----------------------------------------------------------
## Terms that will be included.

Censored_Terms_df = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_R_Censored_Terms_for_Table_Data_2024_03_19.csv")["Term"]

## Merged "natonal signatures" with censored terms 
t0 = pd.merge(Censored_Terms_df,Term_Adoption_by_Country_df,on=["Term"],how="left")

## Calculate term adoption at country-year level
t1 = t0.groupby(['Country','Term','Year']).sum('Percent_Weight').reset_index().sort_values(['Year','Country','Term'])
t1["Year"] = t1["Year"].astype(int)

## Assume time frame of five years
## Create the time window by taking the country-year dataframe.
# e.g., if 1995 is present, then 1990 + 5 = 1995 
t1_1 = t1.eval('Year=Year+1') # e.g., 1994 --> 1995
t1_2 = t1.eval('Year=Year+2')
t1_3 = t1.eval('Year=Year+3')
t1_4 = t1.eval('Year=Year+4')
t1_5 = t1.eval('Year=Year+5') # e.g., 1990 --> 1995

t1_1["Year_Delta"] = 1
t1_2["Year_Delta"] = 2
t1_3["Year_Delta"] = 3
t1_4["Year_Delta"] = 4
t1_5["Year_Delta"] = 5

## Turn country-year term dataframe over five years into one large df
t1_delta = t1_1.append(t1_2).append(t1_3).append(t1_4).append(t1_5)

## Merge back onto the original dataframe on "Term" and altered "Year"
## e.g., for the year 1995, merging onto "1995" (1990+5), "1995" (1991+4),...,"1995" (1994+1)
t2 = pd.merge(t1,t1_delta,on=["Term","Year"],how="outer",suffixes=('_Present', '_Past')).dropna()

## Calculate cosine simlarity score between "national signature" in the present with the past five years
t3 = t2.drop('Term',axis=1).groupby(['Country_Past','Country_Present','Year','Year_Delta']).apply(lambda x: returnCosine(x['Percent_Weight_Past'],x['Percent_Weight_Present'])).rename("Cosine").reset_index()

## Create two dataframes: country compared to past self and country compared to past alter. 
t3_self = t3.query("Country_Past==Country_Present").drop("Year_Delta",axis=1).groupby(['Country_Past','Country_Present','Year']).mean("Cosine").reset_index().drop("Country_Past",axis=1)
t3_other = t3.query("Country_Past!=Country_Present").drop("Year_Delta",axis=1).groupby(['Country_Past','Country_Present','Year']).mean("Cosine").reset_index()

#############
### Output Files
##############
t3_self.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_HNB_RR1_Terms_by_Field_Self_2024_03_19.csv",index=False)
t3_other.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_HNB_RR1_Terms_by_Field_Alter_2024_03_19.csv",index=False)


##########################
### *************************
### Start Here | Read in Files
### *************************
###########################

## Read in files that were just output
t3_self = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_HNB_RR1_Terms_by_Field_Self_2024_03_19.csv")
t3_other = pd.read_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_HNB_RR1_Terms_by_Field_Alter_2024_03_19.csv")

## Create a dataframe that combines country-self with country-alter on the same row to calcualte influence measure.
t4 = pd.merge(t3_other,t3_self,on=["Year","Country_Present"],suffixes=('', '_Self'))
t4["Influence"] = t4["Cosine"]/t4["Cosine_Self"]
t4["Influence_1"] = (t4["Cosine"]+1)/(t4["Cosine_Self"]+1)

## Core country list.
Core_Country = ["US", #US
                  "GB", #UK
                  "CN", #China
                  "DE", #Germany
                  "JP", #Japan
                  "AU", #Australia
                  "AT", #Austria
                  "BE", #Belgium
                  "CA", #Canada
                  "DK", #Denmark
                  "FI", #Finland
                  "FR", #France
                  "IS", #Iceland
                  "IE", #Ireland
                  "IT", #Italy
                  "IL", #Israel
                  "NL", #Netherlands
                  "NZ", #New Zealand
                  "NO", #Norway
                  "PT", #Portugal
                  "SG", #Singapore
                  "KR", #South Korea
                  "ES", #Spain
                  "SE", #Sweden
                  "CH", #Switzerland 
                  "TW" #Taiwan
                  ]

## Identify countries as core and periphery
t4["Receiver_Core_Periphery"] = t4["Country_Present"].apply(lambda x: "Core" if x in Core_Country else "Periphery")
t4["Sender_Core_Periphery"] = t4["Country_Past"].apply(lambda x: "Core" if x in Core_Country else "Periphery")


## Limit years between 1995 (since our analysis starts in 1990) and 2013 (since we have a ten-year forward window for other analyses) 
t5 = t4.query("Year>=1995 & Year<=2013").drop(["Cosine","Cosine_Self","Influence"],axis=1)

## Count the number of years in the dataset with which countries are present, between 1995 and 2013.
## Merge this dataframe back to main dataframe. 
Country_Count_df = t5[["Country_Present","Year"]].drop_duplicates().groupby(["Country_Present"]).count().rename(columns={"Year":"Count_per_Year"}).reset_index()

t5 = pd.merge(t5,Country_Count_df,on=["Country_Present"],how="left")
 
## Test Correlations
# t5.query("Count_per_Year>=15").groupby(["Sender_Core_Periphery","Receiver_Core_Periphery","Year"])["Influence_1"].mean().reset_index().query("Sender_Core_Periphery=='Core' & Receiver_Core_Periphery=='Periphery'").corr()

#############
### Output Files
##############
t5.to_csv("/groups/cjgomez/PROJECT_Phoenix/Output_Data/OUTPUT_Python_HNB_RR1_National_Signature_Influence_2024_03_19.csv",index=False)
