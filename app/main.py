from io import StringIO
import requests as rq
import boto3 
import os
import pandas as pd
from datetime import datetime
import psycopg2 

def get_data():
    #read evevy articles
    apikey = os.environ.get('APIKEY') 
    search_key = os.environ.get('SEARCH_KEY')
    articles_url = f'https://newsapi.org/v2/everything?q={search_key}.&apiKey={apikey}'

    try:
        articles_results = rq.get(articles_url).json()['articles']
        #Remove articles without source id 
        articles_results2 = [ d for d in articles_results if d['source']['id'] != None ] 
        #Flaten the json 
        df_articles = pd.json_normalize(articles_results2, sep='_')
        #Add a datetime column
        df_articles.insert(1,'datetime',str(datetime.now()))
        #Delete any Enter(new line)
        df_articles['content'].replace('\\r|\\n', '' , regex=True,inplace=True)
        articles_csv_buffer = StringIO()
        df_articles.to_csv(articles_csv_buffer,encoding='utf-8',sep='|' ,index=False , header=False) 

    except Exception as err:
        print(f'Error related to {repr(err)}')


    #read source data  
    source_url = f'https://newsapi.org/v2/top-headlines/sources?apiKey={apikey}'
    try:
        source_results = rq.get(source_url).json()['sources']
        df_source = pd.json_normalize(source_results)
        #Add a datetime column
        df_source.insert(1,'datetime',str(datetime.now()))
        source_csv_buffer = StringIO()
        df_source.to_csv(source_csv_buffer,header=False ,sep='|', index=False , encoding='utf-8')
        
    except Exception as err:
        print(f'Error related to {repr(err)}')
    
    return articles_csv_buffer, source_csv_buffer

def upload_to_s3(source , articles, today_date):
    #create a s3 client for connecting to Amazon S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key= os.environ.get('AWS_SECRET_ACCESS_KEY')
         )

    s3_client.put_object(Body=articles.getvalue(), Bucket='neugelb', Key=f'articles_results_{today_date}.csv')
    s3_client.put_object(Body=source.getvalue(), Bucket='neugelb', Key=f'source_results_{today_date}.csv')

def load_s3_to_redshift(today_date):
    #Create connection to Redshift
    conn = psycopg2.connect(
    dbname =  os.environ.get('DB_NAME'), 
    user =  os.environ.get('DB_USER'),
    password = os.environ.get('PASSWORD'),
    host = 'us-east-1.redshift.amazonaws.com',
    port = 5439
    )
    s3_client = boto3.client(
    's3',
    aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key= os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    #Get the list of files in the bucket
    s3_client.list_buckets()
    s3_objects = s3_client.list_objects(
        Bucket = 'mybucket'
    ) 
    #Filter today's files
    files = [obj['Key'] for obj in s3_objects['Contents'] if today_date in obj['Key']]

    if len(files): #if the list contains any file   
        for file_name in files:
            table_name = file_name.split("_",1)[0]  
            s3_location = f's3://mybucket/{file_name}'
            role = 'arn:aws:iam:role/redshift_to_s3'
            #Creating Copy statement
            copy_stmt =f"""
            COPY {table_name}
            FROM '{s3_location}'
            iam_role '{role}'
            delimiter '|'; 
            """
            cursor = conn.cursor() 
            if table_name == 'source':
                cursor.execute(f'truncate table {table_name}')
            cursor.execute('begin;')
            cursor.execute(copy_stmt)
            cursor.execute('commit;')
    else:
        print("There is no file for today.")


def main():
    #Extract data and transformation
    today_date = datetime.today().strftime("%d%m%Y")
    print('Start reading data .... ')
    articles_results , source_results = get_data()
    print('Reading data finished.')
    #Upload data to s3 bucket
    print('\nStart uploading data to s3 .... ')
    upload_to_s3(  source_results , articles_results , today_date)
    print('files uploaded.')
    #Load data to Redshift
    print('\nStart loading to redshift ... ')
    load_s3_to_redshift(today_date)
    print('Loading finished.')


if __name__ == "__main__":
    main()
