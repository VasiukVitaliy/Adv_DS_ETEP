import os
import json
import sys
import dotenv
import certifi
import pandas as pd
import numpy as np
import pymongo
from pathlib import Path
from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

dotenv.load_dotenv()

MONGO_URI = os.getenv("MONGO_DB_URI_CONNECT")

ca=certifi.where()

class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkDataExtract(e, sys)
        
    
    def csv_to_json_convert(self, path: Path):
        try:
            data = pd.read_csv(path)
            conv_data = data.to_dict(orient='records')
            return conv_data
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database = database
            self.collections = collection
            self.records = records
        
            self.mongo_client = pymongo.MongoClient(MONGO_URI)
            self.database = self.mongo_client[self.database]
            self.collections = self.database[self.collections]
            self.collections.insert_many(self.records)
            return self.records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
if __name__ == "__main__":
    FILE_PATH = Path("Network_data\phisingData.csv")
    DATABASE="ADV_ds_proj"
    Collection="NetworkData"
    extractor = NetworkDataExtract()
    records = extractor.csv_to_json_convert(FILE_PATH)
    print(records)
    no_of_records=extractor.insert_data_mongodb(records,DATABASE,Collection)
    print(no_of_records)
        