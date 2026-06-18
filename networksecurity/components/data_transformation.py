from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.utils.main_utils.utils import save_numpy_data_array,save_obj
from networksecurity.logging.logger import logging
import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

class DataTransform:
    def __init__(self, artifact: DataValidationArtifact, config: DataTransformationConfig):
        try:
            self.data_validation_artifact:DataValidationArtifact=artifact
            self.data_transformation_config:DataTransformationConfig=config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def get_data_transformer_object(cls)->Pipeline:
        """
        It initialises a KNNImputer object with the parameters specified in the training_pipeline.py file
        and returns a Pipeline object with the KNNImputer object as the first step.

        Args:
          cls: DataTransformation

        Returns:
          A Pipeline object
        """
        logging.info(
            "Entered get_data_trnasformer_object method of Trnasformation class"
        )
        try:
           imputer:KNNImputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
           logging.info(
                f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )
           processor:Pipeline=Pipeline([("imputer",imputer)])
           return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            train_df = DataTransform.read_data(self.data_validation_artifact.valid_train_data_path)
            test_df = DataTransform.read_data(self.data_validation_artifact.valid_test_data_path)
            
            train_x = train_df.drop(columns = [TARGET_COLUMN], axis=1)
            train_y = train_df[TARGET_COLUMN]
            train_y = train_y.replace(-1, 0)
            
            test_x = test_df.drop(columns = [TARGET_COLUMN], axis = 1)
            test_y = test_df[TARGET_COLUMN]
            test_y = test_y.replace(-1, 0)
            
            preprocessor=self.get_data_transformer_object()
            
            preprocessor_obj = preprocessor.fit(train_x)
            transformed_train_x = preprocessor_obj.transform(train_x)
            transformed_test_x = preprocessor_obj.transform(test_x)
            
            train_arr = np.c_[transformed_train_x, np.array(train_y) ]
            test_arr = np.c_[transformed_test_x, np.array(test_y) ]

            #save numpy array data
            save_numpy_data_array(train_arr, self.data_transformation_config.transformed_train_file_path)
            save_numpy_data_array(test_arr, self.data_transformation_config.transformed_test_file_path)
            save_obj(preprocessor_obj, self.data_transformation_config.transformed_object_file_path)
            
            data_transformation_artifact=DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)