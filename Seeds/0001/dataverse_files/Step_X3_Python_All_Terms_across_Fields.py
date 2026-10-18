###############################
### Modules
###############################

# interactive -t 2:00:00 -m 150G -a charlesgomez

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

import glob

from collections import defaultdict 
import itertools

from nltk.stem import PorterStemmer

from datetime import date

###############################
### PorterStemmer
############################### 

ps = PorterStemmer()

###############################
### Read in Pickle Dictionaries 
############################### 

Filtered_Dict_Inverse_DD = defaultdict(list)
Filtered_Dict_Country_DD = defaultdict(list)
Descriptive_Data_df = pd.DataFrame()

Extracted_Dictionary_List = glob.glob("/groups/cjgomez/PROJECT_Phoenix/Text_Data/INPUT_Python_OpenAlex_Extracted_Terms_*.pbz2")

for file_name in Extracted_Dictionary_List:
	print(file_name)
	try:
		f = bz2.BZ2File(file_name, 'rb')
		Filtered_Dict_Country = cPickle.load(f)
		Filtered_Dict_Inverse = cPickle.load(f)
		Descriptive_Data_ = cPickle.load(f)

		# Double-check
		for key, value in Filtered_Dict_Inverse.items():
			Filtered_Dict_Inverse_DD[key].append(value)

		for key, value in Filtered_Dict_Country.items():
			value_as_list = [value]
			Filtered_Dict_Country_DD[key].append(value_as_list)

		Descriptive_Data_df = pd.concat([Descriptive_Data_df,Descriptive_Data_])

	except Exception as e:
		print(e)
		print("Error with: "+file_name)

Keywords_Dict = dict(Filtered_Dict_Inverse_DD)
for key, value in Keywords_Dict.items():
	Keywords_Dict[key] = sorted(list(set(list(itertools.chain(*value)))))

Country_Dict = dict(Filtered_Dict_Country_DD)
for key, value in Country_Dict.items():
	Country_Dict[key] = sorted(list(set(list(itertools.chain(*value)))))

###############################
### Filter Terms | Origins at 1990 with N = 10 Papers 
############################### 

minimum_number_of_term_apperances = 10
minimum_year = 1990

Keywords_Dict_Filtered = {k:v for k, v in Keywords_Dict.items() if len(v)>=minimum_number_of_term_apperances and int(v[0].split("+")[0])>=minimum_year}

###############################
### Countries of Filtered Keywoard Dictionary  
############################### 

Keywords_List_Flattened_Filtered = list(set(list(itertools.chain.from_iterable([v for k, v in Keywords_Dict_Filtered.items()]))))

Country_Keyword_Dict_Filtered = {work:Country_Dict[work] for work in Keywords_List_Flattened_Filtered}


###############################
### Extracted WikiData from Concept IDs
###############################

Wikidata_df = pd.read_csv('/groups/cjgomez/PROJECT_Phoenix/Input_Data/INPUT_SQL_Extracted_Wikidata_Concept_IDs.csv')
Wikidata_df['work_id'] = Wikidata_df['work_id'].apply(lambda x: x.split(","))
Wikidata_df['display_name'] = Wikidata_df['display_name'].apply(lambda x: ps.stem(x.lower()))

Wikidata_Dict = Wikidata_df[['display_name','work_id']].set_index('display_name')['work_id'].to_dict()

for key, value in Wikidata_Dict.items():
	Wikidata_Dict[key] = sorted(list(set(value)))

Wikidata_Dict_Filtered = {k:v for k, v in Wikidata_Dict.items() if len(v)>=minimum_number_of_term_apperances and int(v[0].split("+")[0])>=minimum_year}

###############################
### Extracted and Wikidata Work IDs to Upload for Citations
###############################

#min_extracted_keywords_work_id = {key:value[0] for key, value in Keywords_Dict_Filtered.items()}
#min_wikiarticles_work_id = {key:value[0] for key, value in Wikidata_Dict_Filtered.items()}

wikiarticles_work_id = list(set(list(itertools.chain(*Wikidata_Dict_Filtered.values()))))
extracted_keywords_work_id = list(set(list(itertools.chain(*Keywords_Dict_Filtered.values()))))

wikiarticles_work_id = [x.split("+")[1] for x in wikiarticles_work_id]
extracted_keywords_work_id = [x.split("+")[1] for x in extracted_keywords_work_id]

upload_work_id = wikiarticles_work_id
upload_work_id.extend(extracted_keywords_work_id)
upload_work_id = list(set(upload_work_id))

upload_work_id_df = pd.DataFrame(upload_work_id,columns=['work_id'])

###############################
### Wikidata Work IDs to Upload for Country Affiliations
###############################
wikidata_workid_list_for_country_identification = list(itertools.chain(*Wikidata_Dict_Filtered.values()))
wikidata_workid_list_for_country_identification = [x.split("+")[1] for x in wikidata_workid_list_for_country_identification]
wikidata_workid_list_for_country_identification = list(set(wikidata_workid_list_for_country_identification))


###############################
### Output
###############################
def add_Zero_for_Single_Digit(x):
	if x<10:
		return '0'+str(x)
	else:
		return x


todays_date = date.today()  
year_ = add_Zero_for_Single_Digit(todays_date.year)
month_ = add_Zero_for_Single_Digit(todays_date.month)
day_ = add_Zero_for_Single_Digit(todays_date.day) 

Filename_Keywords_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Extracted_Terms_and_Wikidata_Dictionary_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".pbz2"
with bz2.BZ2File(Filename_Keywords_Dictionary, 'w') as f:
	cPickle.dump(Keywords_Dict_Filtered, f, protocol=2)
	cPickle.dump(Wikidata_Dict_Filtered, f, protocol=2)
	cPickle.dump(Country_Keyword_Dict_Filtered, f, protocol=2)
f.close()

pd.DataFrame(wikidata_workid_list_for_country_identification,columns=["work_id"]).to_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Work_IDs_WikiData_Terms_for_Country_Affiliation_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".csv",index=False)

upload_work_id_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_All_Work_IDs_Extracted_and_WikiData_Terms_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".csv",index=False)

Descriptive_Data_df.to_csv("/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Descriptive_Data_for_Extracted_Terms_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".csv",index=False)

# ###############################
# ### Output for Country Dictionary Due to Size
# ###############################

# def split(a, n):
#     k, m = divmod(len(a), n)
#     return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

# Country_idx_list = list(split(range(0,len(Country_Dict)), 10))

# for n_ in range(0,10):
# 	Filename_Country_Dictionary_Part_n = "/groups/cjgomez/PROJECT_Phoenix/Compiled_Data/INPUT_Python_OpenAlex_Country_Dictionary_Part_"+str(n_+1)+"_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".pbz2"
# 	with bz2.BZ2File(Filename_Country_Dictionary_Part_n, 'w') as f:
# 		cPickle.dump({k:Country_Dict[k] for k in list(Country_Dict.keys())[min(Country_idx_list[n_]):max(Country_idx_list[n_])+1]}, f, protocol=2)
# 	f.close()
# 	print(n_+1)

#####
# Country_Keywords_Dict_Filtered = {k:[Country_Dict[x] for x in v] for k, v in Keywords_Dict_Filtered.items()}

