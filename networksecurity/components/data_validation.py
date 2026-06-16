from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from networksecurity.logging.logger import logging
import pandas as pd
import os, sys
from scipy.stats import ks_2samp
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 validation_config=DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = validation_config
            schema = read_yaml_file(self.data_validation_config.schema_path)
            self.schema = {list(col.keys())[0]: list(col.values())[0]
                           for col in schema["columns"]}
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(path) -> pd.DataFrame:
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_num_of_cols(self, dataframe: pd.DataFrame) -> bool:
        try:
            num_of_cols_schema = len(self.schema)
            num_of_cols_data = dataframe.shape[1]
            logging.info(f"Required number of columns: {num_of_cols_schema}")
            logging.info(f"DataFrame has columns: {num_of_cols_data}")
            return num_of_cols_data == num_of_cols_schema
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_types_of_cols(self, dataframe: pd.DataFrame) -> bool:
        try:
            cols_data = {col: str(dtype) for col, dtype in dataframe.dtypes.items()}
            return cols_data == self.schema
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_data_drift(self, base_df, current_df, threshold=0.05):
        try:
            status = True
            report = {}
            for col in base_df.columns:
                d1 = base_df[col]
                d2 = current_df[col]
                is_same_dist = ks_2samp(d1, d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False

                report.update({col: {
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": is_found
                }})

            drift_report = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report, content=report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def init_validation(self):
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_data = DataValidation.read_data(train_file_path)
            test_data = DataValidation.read_data(test_file_path)
            logging.info("Train and test data was loaded")

            # Валідація кількості колонок
            num_cols_train_status = self.validate_num_of_cols(train_data)
            logging.info(f"Train data num cols status: {num_cols_train_status}")
            num_cols_test_status = self.validate_num_of_cols(test_data)
            logging.info(f"Test data num cols status: {num_cols_test_status}")

            # Валідація типів колонок
            types_cols_train_status = self.validate_types_of_cols(train_data)
            logging.info(f"Train data type cols status: {types_cols_train_status}")
            types_cols_test_status = self.validate_types_of_cols(test_data)
            logging.info(f"Test data type cols status: {types_cols_test_status}")

            # Загальний статус валідації
            train_valid = num_cols_train_status and types_cols_train_status
            test_valid = num_cols_test_status and types_cols_test_status

            # Шляхи з конфігу
            valid_train_file_path = self.data_validation_config.valid_train_data_filepath
            valid_test_file_path = self.data_validation_config.valid_test_data_filepath
            invalid_train_file_path = self.data_validation_config.invalid_train_data_filepath
            invalid_test_file_path = self.data_validation_config.invalid_test_data_filepath

            # Збереження train даних
            if train_valid:
                dir_path = os.path.dirname(valid_train_file_path)
                os.makedirs(dir_path, exist_ok=True)
                train_data.to_csv(valid_train_file_path, index=False, header=True)
                logging.info(f"Train data saved to valid path: {valid_train_file_path}")
            else:
                dir_path = os.path.dirname(invalid_train_file_path)
                os.makedirs(dir_path, exist_ok=True)
                train_data.to_csv(invalid_train_file_path, index=False, header=True)
                logging.info(f"Train data saved to invalid path: {invalid_train_file_path}")

            # Збереження test даних
            if test_valid:
                dir_path = os.path.dirname(valid_test_file_path)
                os.makedirs(dir_path, exist_ok=True)
                test_data.to_csv(valid_test_file_path, index=False, header=True)
                logging.info(f"Test data saved to valid path: {valid_test_file_path}")
            else:
                dir_path = os.path.dirname(invalid_test_file_path)
                os.makedirs(dir_path, exist_ok=True)
                test_data.to_csv(invalid_test_file_path, index=False, header=True)
                logging.info(f"Test data saved to invalid path: {invalid_test_file_path}")

            # Drift тільки якщо обидва валідні
            data_drift_status = False
            if train_valid and test_valid:
                data_drift_status = self.detect_data_drift(base_df=train_data, current_df=test_data)
                logging.info(f"Data drift detected: {data_drift_status}")
            else:
                logging.warning("Skipping drift detection: one or both datasets are invalid")

            validation_status = train_valid and test_valid and not data_drift_status

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                valid_train_data_path=valid_train_file_path,
                valid_test_data_path=valid_test_file_path,
                invalid_train_data_path=invalid_train_file_path,
                invalid_test_data_path=invalid_test_file_path,
                drift_data_report_path=self.data_validation_config.drift_report_file_path,
            )

            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)