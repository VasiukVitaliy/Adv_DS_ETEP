from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    train_file_path: str
    test_file_path: str
    
@dataclass
class DataValidationArtifact:
    validation_status: str
    valid_test_data_path: str
    valid_train_data_path: str
    invalid_test_data_path: str
    invalid_train_data_path: str
    drift_data_report_path: str