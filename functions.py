import requests
import json
import polars as pl
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

#loading dotenv
load_dotenv()

def getVideoRecords(response: requests.models.Response) -> list:

    """
        Function to extract YouTube video data from GET request response

        Dependencies: 
            - getVideoIDs()
    """
    
    video_record_list = []

    try:
        data = response.json()

    except ValueError:
        print("⚠️ Response is not valid JSON:", response.text)
        return video_record_list

    if "items" not in data:
        print("⚠️ Unexpected response structure:", data)
        return video_record_list
    
    
    for raw_item in json.loads(response.text)['items']:
    
        # Note: playlistItems only returns videos
           
        video_record = {}
        video_record['video_id'] = raw_item['contentDetails']['videoId'] #The ID that YouTube uses to uniquely identify a video
        video_record['datetime'] = raw_item['snippet']['publishedAt'] #The date and time that the item was added to the playlist.
        video_record['title'] = raw_item['snippet']['title'] #The item's title
        video_record['description'] = raw_item['snippet']['description'] # The item's description.

        
        video_record_list.append(video_record)

    return video_record_list


def getVideoID():
    """
        Function to return all video IDs for my YouTube channel

        Dependencies: 
            - getVideoRecords()
    """


    playlist_id = os.getenv("PLAYLIST_ID")# my YouTube playlist ID
    page_token = None # initialize page token
    url = 'https://www.googleapis.com/youtube/v3/playlistItems' # Access playlist items (endpoint)
    # testurl = https://www.googleapis.com/youtube/v3/channels?part=statistics&id=''-QPj48_A&key=''

    my_key = os.getenv('YT_API_KEY') #youtube_api

    # extract video data across multiple search result pages
    video_record_list = []

    while page_token != 0:
        params = {
            "key": my_key, 
            'playlistId': playlist_id, 
            'part': ["snippet","contentDetails"], 
            'maxResults':25, 
            'pageToken': page_token
        }
        response = requests.get(url, params=params)

        # append video records to list
        video_record_list += getVideoRecords(response)

        try:
            # grab next page token
            page_token = json.loads(response.text)['nextPageToken']
        except:
            # if no next page token kill while loop
            page_token = 0

    # write videos ids as parquet file
    pl.DataFrame(video_record_list).write_parquet('data/video-ids.parquet')


def extractTranscriptText(transcript: list) -> str:
    """
        Function to extract text from transcript dictionary

        Dependers:
            - getVideoTranscripts()
    """
    
    text_list = [transcript[i]['text'] for i in range(len(transcript))]
    return ' '.join(text_list)


def getVideoTranscripts():
    """
        Function to extract transcripts for all video IDs stored in "data/video-ids.parquet"

        Dependencies:
            - extractTranscriptText()
    """


    df = pl.read_parquet('data/video-ids.parquet')

    #For debugging
    # if df.is_empty():
    #     print(" No video data found, skipping transform step.")


    transcript_text_list = []

    for i in range(len(df)):

        # try to extract captions
        try:
            transcript = YouTubeTranscriptApi.get_transcript(df['video_id'][i])
            transcript_text = extractTranscriptText(transcript)
        # if not available set as n/a
        except:
            transcript_text = "n/a"
        
        transcript_text_list.append(transcript_text)

    # add transcripts to dataframe
    df = df.with_columns(pl.Series(name="transcript", values=transcript_text_list))

    # write dataframe to file (incase of dealing with big data better to store in remote storage eg S3 bcuket)
    df.write_parquet('data/video-transcripts.parquet')


def handleSpecialStrings(df: pl.dataframe.frame.DataFrame) -> pl.dataframe.frame.DataFrame:
    """
        Function to replace special character strings in video transcripts and titles
        
        Dependers:
            - transformData()
    """

    special_strings = ['&#39;', '&amp;'] #apostrophe, ampersand
    special_string_replacements = ["'", "&"]

    for i in range(len(special_strings)):
        df = df.with_columns(df['title'].str.replace(special_strings[i], special_string_replacements[i]).alias('title'))
        df = df.with_columns(df['transcript'].str.replace(special_strings[i], special_string_replacements[i]).alias('transcript'))

    return df

def setDatatypes(df: pl.dataframe.frame.DataFrame) -> pl.dataframe.frame.DataFrame:
    """
        Function to change data types of columns in polars data frame containing video IDs, dates, titles, and transcripts

        Dependers:
            - transformData()
    """

    # change datetime to Datetime dtype
    df = df.with_columns(pl.col('datetime').cast(pl.Datetime))

    return df


def transformData():
    """
        Function to preprocess video data

        Dependencies:
            - handleSpecialStrings()
            - setDatatypes()
    """

    df = pl.read_parquet('data/video-transcripts.parquet')

    if df.is_empty():
        print(" No video data found, skipping transform step.")

    df = handleSpecialStrings(df)
    df = setDatatypes(df)

    df.write_parquet('data/video-transcripts.parquet')

def createTextEmbeddings():
    """
        Function to generate text embeddings of video titles and transcripts
    """

    # read data from file
    df = pl.read_parquet('data/video-transcripts.parquet')

    # define embedding model and columns to embed
    model_emb = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    # model = SentenceTransformer('all-MiniLM-L6-v2')

    column_name_list = ['title', 'transcript']

    for column_name in column_name_list:
        # generate embeddings
        # embedding_arr = model.encode(df[column_name].to_list())
        embedding_arr = model_emb.embed_documents(df[column_name].to_list())

        # store embeddings in a dataframe
        schema_dict = {column_name+'_embedding-'+str(i): float for i in range(embedding_arr.shape[1])}
        df_embedding = pl.DataFrame(embedding_arr, schema=schema_dict)

        # append embeddings to video index
        df = pl.concat([df, df_embedding], how='horizontal')

    # write data to file
    df.write_parquet('data/video-index.parquet')