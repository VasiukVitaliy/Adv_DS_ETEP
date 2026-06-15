import os
from datetime import datetime
from networksecurity.constants import training_pipeline

class TrainingPipelineConfig:
    def __init__(self, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp: str = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_path = os.path.join(self.artifact_name, self.timestamp)
        self.model_dir = "final_model"

class DataIngestionConfig:
    def __init__(self, training_pipe_config: TrainingPipelineConfig):
        self.data_ingestion_path = os.path.join(
            training_pipe_config.artifact_path,
            training_pipeline.DATA_INGESTION_DIR_NAME
        )
        self.feature_store_file_path = os.path.join(
            self.data_ingestion_path,
            training_pipeline.DATA_INGESTION_FEATURE_DIR,
            "data.csv"
        )
        self.training_file_path = os.path.join(
            self.data_ingestion_path,
            training_pipeline.TRAIN_FILE_NAME
        )
        self.test_file_path = os.path.join(
            self.data_ingestion_path,
            training_pipeline.TEST_FILE_NAME
        )
        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DB_NAME