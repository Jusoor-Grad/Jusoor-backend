"""
    script to import familiar mental health conversation to be used for few-shot prompting for the mental health chatbot
"""
from typing import Any, List
from django.core.management.base import BaseCommand, CommandParser
from langchain_core.documents import Document
import json
from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from jusoor_backend.settings import env
import pandas as pd
import profanity_check

class Command(BaseCommand):

    help = "Command to load reference JSON file to generate embeddings for mental health conversations"


    def add_arguments(self, parser: CommandParser) -> None:
        pass
        # parser.add_argument('--path', '-p', type=str, help="Path to the file containing the embeddings", required=True)

    def handle(self, *args: Any, **options: Any) -> str | None:
        
        # self.stdout.write(f"Loading embeddings from file:  {options['path']} ..", style_func=self.style.SUCCESS)
        
        with open('combined_dataset.json') as f:
            data = f.readlines()

        results = [  json.loads(row.strip()) for row in data]
        results = [{"context": row['Context'], "response": row['Response']} for row in results]

        # Step 2: Convert to DataFrame
        df = pd.DataFrame(results)

        print('BEFORE:', df.shape)

        # Step 3: Remove duplicates
        dropped_duplicates = df.drop_duplicates(subset=['context'], keep='first')

        filtered_profanity_df = dropped_duplicates[dropped_duplicates['context'].apply(lambda x: profanity_check.predict([x])[0] == 0)]
        filtered_profanity_df = filtered_profanity_df.drop_duplicates(subset=['context'], keep='first')
        print('AFTER DROPPING PROFANITY+DUPLICATIONS:', filtered_profanity_df.shape)
        
        results = [
            Document(page_content= row[1]['context'], metadata={'response': row[1]['response'], 'channel': "references"}) for row in filtered_profanity_df.iterrows()
        ]

        # print('AFTER:', len(results), results[0])
        # # init the PGVector store and the embeddings
        

        
        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            host= env('DB_HOST'),
            port= env('DB_PORT'),
            database= env('DB_NAME'),
            user= env('DB_USER'),
            password= env('DB_PASS'),
            driver='psycopg2'

        )

        embeddings = OpenAIEmbeddings(openai_api_key=env('OPENAI_KEY'))

        vector_store = PGVector(
            connection_string= CONNECTION_STRING,
            collection_name= env('EMBEDDING_COLLECTION_NAME'),
            embedding_function= embeddings
        )

        vector_store.add_documents(results)

   