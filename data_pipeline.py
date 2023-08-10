from functions import *
import time
import datetime

#printing time pipeline begins to run
print("Starting data pipeline at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('-----------------------------------------------------------------------------------')


#Extracting the video ID's from videos in Youtube
t0 = time.time()

getVideoID()

t1 = time.time()
print("-------Video ID's downloaded in", str(t1-t0), "seconds", "\n")

#Extracting the transcripts of each video
t0 = time.time()

getVideoTranscripts()

t1= time.time()
print("------Transcripts downloaded------")

# Data Transformation i.e data preprocessing
transformData()
print("-------Data Transformation complete!!-------")

#Generate Text Embeddings
createTextEmbeddings()
print("----Text Embeddings Generated----")


