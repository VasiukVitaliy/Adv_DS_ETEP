import os
import sys

from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransform
from networksecurity.components.model_training import ModelTraining

from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainingConfig
)
from networksecurity.cloud.s3_sync import artifact_to_s3, model_to_s3

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from dotenv import load_dotenv
load_dotenv()

class TrainingPipeline:
    def __init__(self):
        self.training_pipe_config = TrainingPipelineConfig()
        
    def init_ingestion(self):
        try:
            self.data_ingestion_config=DataIngestionConfig(training_pipe_config=self.training_pipe_config)
            data_ingestion=DataIngestion(self.data_ingestion_config)
            logging.info("Initiate the data ingestion")
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info("Data Initiation Completed")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def init_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            data_validation_config = DataValidationConfig(self.training_pipe_config)
            data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
            logging.info("Initiate the data validation")
            data_validation_artifact=data_validation.init_validation()
            logging.info("Data Validation Completed")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def init_transform(self, data_validation_artifact):
        try:
            data_transformation_config = DataTransformationConfig(self.training_pipe_config)
            data_transformation = DataTransform( data_validation_artifact, data_transformation_config)
            logging.info("Initiate the data transformation")
            data_transformation_artifact=data_transformation.initiate_data_transformation()
            logging.info("Data Transformation Completed")
            return  data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def init_train(self, data_transformation_artifact):
        try:
            model_training_config = ModelTrainingConfig(self.training_pipe_config)
            model_training = ModelTraining(model_training_config, data_transformation_artifact)
            logging.info("Initiate the model experiments")
            model_training_artifact=model_training.init_model_trainer()
            logging.info("Model experimenting Completed")
            return model_training_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def save_artifacts_to_s3(self):
        try:
            artifact_to_s3(self.training_pipe_config.artifact_path, 
                           self.training_pipe_config.pipeline_name,
                           "artifacts"
                           )
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def save_model_to_s3(self):
        try:
            model_to_s3("final_model/full_model.pkl", 
                           self.training_pipe_config.pipeline_name,
                           "artifacts"
                           )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        try:
            data_ingestion_artifact=self.init_ingestion()
            data_validation_artifact=self.init_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact=self.init_transform(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.init_train(data_transformation_artifact=data_transformation_artifact)
            self.save_artifacts_to_s3()
            self.save_model_to_s3()
            
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)