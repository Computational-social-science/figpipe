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

## pytextrank
# Setting up pytextrank
# Source - https://github.com/DerwenAI/pytextrank
# apptainer run ~/python38_latest.sif python3 -m pip install pytextrank --user
import pytextrank

# apptainer run ~/python38_latest.sif python3 -m spacy download en_core_web_sm --user
import spacy

from rake_nltk import Rake

# apptainer run ~/python38_latest.sif python3 -m pip install yake --user
import yake 

# apptainer run ~/python38_latest.sif python3 -m pip install textacy --user 
import textacy 

# apptainer run ~/python38_latest.sif python3 -m pip install multi-rake --user 
from multi_rake import Rake as MultiRake

# apptainer run ~/python38_latest.sif python3 -m pip install pybind --user  
# apptainer run ~/python38_latest.sif python3 -m pip install fasttext --user  
import fasttext

# Setting up pyate
# source: https://github.com/kevinlu1248/pyate
# singularity run python38_202206.sif python3 -m spacy download en_core_web_sm
# singularity run python38_202206.sif python3 -m pip install --user pyate 
from pyate import combo_basic
import spacy

###############################
### Input Discipline
###############################
discipline = str(sys.argv[1])

try:
	Total_N = str(sys.argv[2])
	n_ = str(sys.argv[3])
except:
	Total_N = None
	n_ = None


#discipline = 'C512968161'
num_cpu_workers = 10

start_time = time.time()

###############################
### Connections
###############################

cursor = connect(aws_access_key_id='**********',
                 aws_secret_access_key='**********',
                 s3_staging_dir='**********',
                 region_name='**********').cursor()

conn = connect(aws_access_key_id='**********',
                 aws_secret_access_key='**********',
                 s3_staging_dir='**********',
                 region_name='**********')


###############################
### PorterStemmer
############################### 
ps = PorterStemmer()

###############################
### Load SpaCy English Model
############################### 
# load a spaCy model, depending on language, scale, etc.
nlp_en = spacy.load("en_core_web_sm")

###############################
### Query in text data from Field (all available years). 
###############################



if n_==None or n_=='':
	#text_sql = '''
	#select * from mag_staging.project_phoenix_text_data
	#where concept_id = 'FIELDIDHERE'
	#'''

	text_sql = '''
	with work_concept_id as (SELECT DISTINCT work_id 
	FROM "open_alex"."works_concepts" 
	where cast(score as double) > 0 
	AND concept_id = 'https://openalex.org/FIELDIDHERE')
	select * from mag_staging.project_phoenix_text_data
	JOIN work_concept_id
	ON work_concept_id.work_id = project_phoenix_text_data.work_id
	WHERE concept_id = 'FIELDIDHERE'
	'''
else: 
	
	# text_sql = '''
	# WITH ChunkedData AS
	# (
	#     SELECT 
	#         NTILE(TOTALHERE) OVER (ORDER BY work_id) as Chunk,
	#         * 
	#  	from mag_staging.project_phoenix_text_data
	# where concept_id = 'FIELDIDHERE'
	# )
	# SELECT * 
	# FROM ChunkedData
	# WHERE Chunk = NHERE
	# '''
	
	# NOTE - NTILE() starts its count at 1 not 0. 
	text_sql = '''
	with work_concept_id as (SELECT DISTINCT work_id 
	FROM "open_alex"."works_concepts" 
	where cast(score as double) > 0 
	AND concept_id = 'https://openalex.org/FIELDIDHERE'), 
	ChunkedData AS
	(
	    SELECT 
	        NTILE(TOTALHERE) OVER (ORDER BY project_phoenix_text_data.work_id) as Chunk,
	        * 
	 	from mag_staging.project_phoenix_text_data
	JOIN work_concept_id
	ON work_concept_id.work_id = project_phoenix_text_data.work_id
	WHERE concept_id = 'FIELDIDHERE'
	)
	SELECT * 
	FROM ChunkedData
	WHERE Chunk = NHERE
	'''

	text_sql = text_sql.replace('NHERE',n_).replace('TOTALHERE',Total_N)


try_again=0
Text_df = pd.DataFrame()
while try_again<=10 and Text_df.shape[0]==0:
	try:
		Text_df  = pd.read_sql(text_sql.replace('FIELDIDHERE',discipline), conn)
		try_again = 1000
	except:
		try_again+=1
		print(try_again)
		time.sleep(30)

Text_df = Text_df.dropna()

Text_df["year"] = Text_df["year"].astype(int)
del Text_df["concept_id"]

Text_df["Text"] = Text_df["title"].apply(lambda x: x + ". ") + Text_df['abstract'].apply(lambda x: x.replace("Abstract ",""))

###############################
### Prepare Term Extraction
###############################

# Textrank
try:
	nlp_en.add_pipe("textrank")
except:
	next 

# Multi-Rake
multirake = MultiRake(min_chars=3,max_words=5)

# Yake
yake_kw_extractor =  yake.KeywordExtractor(lan="en",n=5,top=20)

# Textacy
textacy_en = textacy.load_spacy_lang("en_core_web_sm") 

# Language Detection
# https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
pretrained_lang_model = "/groups/cjgomez/PROJECT_Phoenix/FastText_Pretrained/lid.176.bin"
language_model = fasttext.load_model(pretrained_lang_model)

###############################
### Extract Terms in Parallel
###############################

def process_text(input_text):
	try:
		## Pre-processing

		# Extract terms within parantheses that are often key phrases
		# Keyword needs to be at least three characters long. 
		term_parantheses = re.findall('\(.*?\)',input_text)
		term_parantheses = [ps.stem(x.replace("(","").replace(")","")) for x in term_parantheses if len(x.split(" "))<2]

		## Language Detect 
		language_prediction = language_model.predict(input_text, k=1)
		language_prediction = language_prediction[0][0].split("__label__")[1]

		## TextRank
		# https://towardsdatascience.com/textrank-for-keyword-extraction-by-python-c0bae21bcec0
		doc = nlp_en(input_text)
		TextRank_list = list(set([ps.stem(term.text.lower()) for term in doc._.phrases]))

		## RAKE 
		# https://towardsdatascience.com/introducing-keyllm-keyword-extraction-with-llms-39924b504813
		#r = Rake()
		#r.extract_keywords_from_text(input_text)
		#RAKE_list = r.get_ranked_phrases()
		#RAKE_list = [ps.stem(x) for x in RAKE_list]

		## Multi-RAKE
		# https://github.com/vgrabovets/multi_rake
		MultiRAKE_list = multirake.apply(input_text)
		MultiRAKE_list = [ps.stem(x[0]) for x in MultiRAKE_list]

		## YAKE
		# https://liaad.github.io/yake/
		YAKE_list = yake_kw_extractor.extract_keywords(input_text)
		YAKE_list = [ps.stem(x[0].lower()) for x in YAKE_list]

		## Textacy
		Textacy_doc = textacy.make_spacy_doc(input_text, lang=textacy_en) 
		Textacy_list = textacy.extract.keyterms.textrank(Textacy_doc,topn=20) #FIX NUMBER OF NGRAMS
		Textacy_list = [ps.stem(x[0].lower()) for x in Textacy_list]

		## Combine Lists | Need a majority vote, at least three appearance out of the four to be included. 
		Combined_list = dict(Counter(YAKE_list) + Counter(MultiRAKE_list) + Counter(TextRank_list) + Counter(Textacy_list))
		Combined_list = [x for x, y in Combined_list.items() if y>=3]

		if term_parantheses!=['']:
			Combined_list.extend(term_parantheses)

		Combined_list = list(set(Combined_list))
	except Exception as e: 
		print(e)
		Combined_list = []
	return Combined_list

pandarallel.initialize(use_memory_fs=False,nb_workers=num_cpu_workers)
Text_df['Terms_Extracted'] = Text_df['Text'].parallel_apply(process_text)

###############################
### Identify Common Candidate Terms | Remove Phrases, N >= 10 Documents, and len(term) > 1
###############################
All_Terms_List = list(itertools.chain.from_iterable(Text_df['Terms_Extracted'].values.tolist()))
All_Terms_Counter = Counter(All_Terms_List)
remove_phrases = ['role','effect','structur','develop','character','water','temperatur','product','review','mechan','activ','reaction','pressur','high','low','singl','applic','format','influenc','studi','face','life']
#All_Terms_Filtered = [x for x, count in All_Terms_Counter.items() if count >= 10 and len(x)>1 and x not in remove_phrases]
All_Terms_Filtered = [x for x, count in All_Terms_Counter.items() if len(x)>1 and x not in remove_phrases]

# if n_==None or n_=='':
# 	All_Terms_Filtered = [x for x, count in All_Terms_Counter.items() if count > 1 and len(x)>1 and x not in remove_phrases]
# # Need to keep all terms if splitting the corpus into different parts to avoid missing a term.
# else:
# 	All_Terms_Filtered = [x for x, count in All_Terms_Counter.items() if len(x)>1 and x not in remove_phrases]


###############################
### Extract Filtered Terms in Parallel
###############################
def Keep_Filtered_Terms(x):
	try:
		return list(set(All_Terms_Filtered)&set(x))
	except:
		return []

pandarallel.initialize(use_memory_fs=False,nb_workers=num_cpu_workers)
Text_df['Terms_Extracted_Filtered'] = Text_df['Terms_Extracted'].parallel_apply(Keep_Filtered_Terms)

###############################
### Create Dictionary of Year-Work IDs to Terms
###############################
Filtered_Text_df = Text_df[Text_df.astype(str)['Terms_Extracted_Filtered'] != '[]']
Filtered_Text_df = Filtered_Text_df.loc[:, ~Filtered_Text_df.columns.duplicated()]
Filtered_Text_df["Year_Work_ID"] = Filtered_Text_df["year"].astype(str) + "+" + Filtered_Text_df["work_id"] 

Filtered_Dict = Filtered_Text_df[["Year_Work_ID",'Terms_Extracted_Filtered']].set_index("Year_Work_ID").to_dict()['Terms_Extracted_Filtered']

###############################
### Flip the Dictionary | Create Dictionary of Terms to Year-Work IDs
###############################
Filtered_Dict_Inverse = {}
for k,v in Filtered_Dict.items():
    for x in v:
        Filtered_Dict_Inverse.setdefault(x, []).append(k)

###############################
### Sort the Contents of Flipped Dictionary so Earliest Year-Work ID is First
###############################
Filtered_Dict_Inverse = {k:sorted(v) for k, v in Filtered_Dict_Inverse.items()}

###############################
### Create Dictionary of Year-Work IDs to Country
###############################
Filtered_Dict_Country = Filtered_Text_df[["Year_Work_ID",'country']].set_index("Year_Work_ID").to_dict()['country']

###############################
### Descriptive Data
###############################
try:
	Descriptive_Data_df = pd.DataFrame.from_dict({"Concept_ID":discipline,
		"N_All_Filtered_Terms":len(All_Terms_Filtered),
		"N_All_Extracted_Terms":len(All_Terms_List),
		"N_All_Unique_Terms":len(All_Terms_Counter),
		"N_All_Tokens":Text_df["Text"].apply(lambda x: len(x.split(" "))).sum(),
		"N_Original_Documents":Text_df.shape[0],
		"N_Filtered_Documents":Filtered_Text_df.shape[0],
		"Minimum_Publication_Year":Text_df["year"].min(),
		"Maximum_Publication_Year":Text_df["year"].max(),
		"Minimum_Publication_Year_Filtered":Filtered_Text_df["year"].min(),
		"Maximum_Publication_Year_Filtered":Filtered_Text_df["year"].max()},orient='index').T

except Exception as e:
	print(e)
	Descriptive_Data_df = pd.DataFrame()

print("--- %s seconds ---" % (time.time() - start_time))


###############################
### Output
###############################
if n_==None or n_=='':
	Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Text_Data/INPUT_Python_OpenAlex_Extracted_Terms_"+discipline+".pbz2"
else:
	Filename_Dictionary = "/groups/cjgomez/PROJECT_Phoenix/Text_Data/INPUT_Python_OpenAlex_Extracted_Terms_"+discipline+"_"+n_+".pbz2"

with bz2.BZ2File(Filename_Dictionary, 'w') as f:
	cPickle.dump(Filtered_Dict_Country, f, protocol=2)
	cPickle.dump(Filtered_Dict_Inverse,f, protocol=2)
	cPickle.dump(Descriptive_Data_df,f, protocol=2)
f.close()

###############################
### Test
###############################
# f = bz2.BZ2File(Filename_Dictionary, 'rb')
# Test_Filtered_Dict_Country = cPickle.load(f)
# Test_Filtered_Dict_Inverse = cPickle.load(f)
# Test_Descriptive_Data_df = cPickle.load(f)
