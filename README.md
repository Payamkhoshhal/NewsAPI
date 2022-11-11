# NewsAPI
## Section 1: Python Script 

### Architecture:

Data will be extracted from the NewsApi and after some transformation to data, it will be stored in the Amazon S3 bucket in different CSV files. Then files will be inserted to Amazon Redshift. Due to the performance reasons I decided to don’t insert the date directly into the amazon Redshift, because copying files from S3 to Redshift is fast enough and the data will be archived in S3 bucket.

![image](https://user-images.githubusercontent.com/94925635/201370049-23ef3640-f1bb-4c28-a25e-d76d9a10fbe9.png)



### Explanation:

First of all I created an account in NewsApi website and recieved an ApiKey. I used python for this project. The whole project is divided into three steps and these three steps implemented in three functions. get_date(), upload_to_s3(), and load_s3_to_redshift(). 

I suppose that this ETL project will execute on a daily bases. Files will be stored by name and current date like: articles_results_21102022.csv that means the file is related to articles for 21.10.2022.

### Description about get_date() Function:

In this function two environment variables for apikey and search_key (‘searchkeyword’) are used. I used requests library for reading data related to articles and source from everything and sources.
Then in articles data, those records which don’t have source id are omitted with a list comprehension. With pandas library and JSON normalize function data is flatten. After a careful investigation in data, I realized that there are some unexpected Enter (new line) in one of our columns, so I removed the Enter character. I decided to add one column to data for having the datetime so we can easily understand which record is related to which date.
The same process is done for source data. The output of this function is two CSV files which will be passed to the next function and are ready to insert into a S3 bucket for archiving purposes.



### Description about upload_to_s3():

This function get three objects. Two CSV files for articles and source data and a variable which contains today’s date for making the proper file name in S3 bucket. Here I used boto3 library to connect to AWS S3 service. A s3_client was created with AWS access_key and secret_key which they will be read from environment variables.
Then I used put_object to put the data in the bucket that I created for this project. The picture below shows a sample data which were uploaded to the S3 via this function:



![image](https://user-images.githubusercontent.com/94925635/201370134-3d30042a-e8da-4eea-b603-fa7e04d79dd7.png)

















### Description about load_s3_to_redshift():

In this function I used another library named psycopg3 for connecting to amazon Redshift. So we need to prepare a connection to Redshift with proper username, database name, password, port, and host. These variables are set as environment variables. After creating the connection to Redshift, we need to know which files have to be loaded into which table. So with boto3 I get the list of the files and find those files which are for today. Also, the table name can be detected from the first word of the file name. According to the above picture, the first two files are belonged to articles table.
Since we have the connection and file name we can make our Copy statement and execute it.

## Section 2: How to Run

I created a docker file. All the environment variables should be sat in the docker file. First we need to create an image from docker file:
           
             $ docker build -t name .

After creating the image we can run the image:
            
             $ docker run name

#### Note: Because of the security reason, I changed iam role and host name in the python code.  

