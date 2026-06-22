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
        
class DataValidationConfig:
    def __init__(self, training_pipe_config: TrainingPipelineConfig):
        self.data_validation_dir = os.path.join(
            training_pipe_config.artifact_path,
            training_pipeline.DATA_VALIDATION_DIR_NAME
        )
        self.valid_data_dir = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_VALID_DIR
        )
        self.invalid_data_dir = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_INVALID_DIR
        )
        self.valid_train_data_filepath = os.path.join(
            self.valid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )
        self.valid_test_data_filepath = os.path.join(
            self.valid_data_dir, training_pipeline.TEST_FILE_NAME
        )
        self.invalid_train_data_filepath = os.path.join(
            self.invalid_data_dir, training_pipeline.TRAIN_FILE_NAME
        )
        self.invalid_test_data_filepath = os.path.join(
            self.invalid_data_dir, training_pipeline.TEST_FILE_NAME
        )
        self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME,
        )
        self.schema_path = training_pipeline.SCHEMA_FILE_PATH
        
class DataTransformationConfig:
     def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_transformation_dir: str = os.path.join( 
                training_pipeline_config.artifact_name,
                training_pipeline.DATA_TRANSFORMATION_DIR_NAME
            )
        self.transformed_train_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TRAIN_FILE_NAME.replace("csv", "npy")
            )
        self.transformed_test_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TEST_FILE_NAME.replace("csv", "npy")
            )
        self.transformed_object_file_path: str = os.path.join(
            self.data_transformation_dir, 
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,
            training_pipeline.PREPROCESSING_OBJECT_FILE_NAME
            )
        
class ModelTrainingConfig:
    def __init__(self, train_pipeline_config: TrainingPipelineConfig):
        self.model_training_artifact_dir = os.path.join(
            train_pipeline_config.artifact_name,
            training_pipeline.MODEL_TRAINER_DIR_NAME
        )
        self.model_file_path = os.path.join(
            self.model_training_artifact_dir,
            training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR,
            training_pipeline.MODEL_FILE_NAME
        )
    
        self.expected_accuracy: float = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE
        self.overfitting_underfitting_threshold = training_pipeline.MODEL_TRAINER_OVER_FIITING_UNDER_FITTING_THRESHOLD