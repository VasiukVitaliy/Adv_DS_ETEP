from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URI_CONNECT")
if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URI_CONNECT is not set in environment variables")


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        try:
            self.config = config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            collection_name = self.config.collection_name
            db_name = self.config.database_name
            mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            print(mongo_client.server_info()) 
            try:
                collection = mongo_client[db_name][collection_name]
                logging.info(f"Loaded data from [{collection_name}] in [{db_name}]")
                df = pd.DataFrame(list(collection.find()))
            finally:
                mongo_client.close()

            if "_id" in df.columns.tolist():
                df = df.drop(columns=["_id"])

            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            feature_file_path = self.config.feature_store_file_path
            dir_path = os.path.dirname(feature_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_file_path, index=False, header=True)
            logging.info(f"Saved data in {feature_file_path}")
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_train_test_data(self, dataframe: pd.DataFrame) -> DataIngestionArtifact:
        try:
            train_path = self.config.training_file_path
            test_path = self.config.test_file_path

            train_data, test_data = train_test_split(
                dataframe, test_size=self.config.train_test_split_ratio
            )
            logging.info("Data was split")

            os.makedirs(os.path.dirname(train_path), exist_ok=True)

            train_data.to_csv(train_path, index=False, header=True)
            logging.info(f"Saved train data to {train_path}")
            test_data.to_csv(test_path, index=False, header=True)
            logging.info(f"Saved test data to {test_path}")

            artifact = DataIngestionArtifact(
                train_file_path=train_path,
                test_file_path=test_path  # було train_path — баг
            )
            logging.info("Created data ingestion artifact")
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data = self.export_collection_as_dataframe()
            df = self.export_collection_as_feature_store(data)
            return self.split_train_test_data(df)
        except Exception as e:
            raise NetworkSecurityException(e, sys)