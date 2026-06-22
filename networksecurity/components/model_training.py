from networksecurity.exceptions.exception import NetworkSecurityException
from networksecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact
from networksecurity.entity.config_entity import ModelTrainingConfig
from networksecurity.utils.main_utils.utils import load_numpy_array
from networksecurity.utils.ml_utils.models.estimator import evaluate_models, NetworkModel
from networksecurity.utils.ml_utils.metrics.classification_metrics import get_classification_scores
from networksecurity.utils.main_utils.utils import load_obj, save_obj
from networksecurity.logging.logger import logging
import sys, os
import mlflow, dagshub
from urllib.parse import urlparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)


class ModelTraining:
    def __init__(self, config, artifact):
        try:
            self.config = config
            self.artifact = artifact
            logging.info("ModelTraining initialized with config and artifact")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_model(self, model, train_report: dict, test_report: dict, params):
        try:
            logging.info("Starting MLflow tracking run")
            dagshub.init(repo_owner='vitaliy98765321', repo_name='Adv_DS_ETEP', mlflow=True)
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

            with mlflow.start_run():
                for key, val in train_report.items():  # FIX: .items() потрібен для dict
                    mlflow.log_metric("_".join(["train", key]), val)
                    logging.info(f"Logged train metric {key}={val}")

                for key, val in test_report.items():  # FIX: .items() потрібен для dict
                    mlflow.log_metric("_".join(["test", key]), val)
                    logging.info(f"Logged test metric {key}={val}")

                mlflow.log_params(params)
                logging.info(f"Logged params: {params}")

                if tracking_url_type_store != "file":
                    mlflow.sklearn.log_model(model, "model", registered_model_name=type(model).__name__)
                    logging.info("Model registered in MLflow registry")
                else:
                    mlflow.sklearn.log_model(model, "model")
                    logging.info("Model logged to local MLflow store")

            logging.info("MLflow tracking run completed successfully")
        except Exception as e:
            logging.error(f"Error while tracking model in MLflow: {e}")
            raise NetworkSecurityException(e, sys)

    def train_model(self, X_train, y_train, X_test, y_test):
        try:
            logging.info("Starting model training process")

            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
            params = {
                "Decision Tree": {
                    'criterion': ['gini', 'entropy', 'log_loss'],
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 128, 256]
                },
                "Gradient Boosting": {
                    'learning_rate': [.1, .01, .05, .001],
                    'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "Logistic Regression": {},
                "AdaBoost": {
                    'learning_rate': [.1, .01, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                }
            }

            logging.info(f"Models to evaluate: {list(models.keys())}")

            model_report: dict = evaluate_models(
                X_train=X_train, y_train=y_train,
                X_test=X_test, y_test=y_test,  # FIX: був x_test (NameError, не визначено)
                models=models, params=params
            )
            logging.info("Model evaluation completed, selecting best model")

            best_model_name = max(model_report, key=lambda m: model_report[m]["test_score"])
            best_report = model_report[best_model_name]  # FIX: max() повертає КЛЮЧ, не значення

            best_model = best_report["model"]
            best_params = best_report["best_params"]

            logging.info(f"Best model selected: {best_model_name} with params: {best_params}")

            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)
            logging.info("Generated predictions on train and test sets")

            classification_train_metric = get_classification_scores(y_true=y_train, y_pred=y_train_pred)
            classification_test_metric = get_classification_scores(y_true=y_test, y_pred=y_test_pred)
            logging.info(f"Train metrics: {classification_train_metric.__dict__}")
            logging.info(f"Test metrics: {classification_test_metric.__dict__}")

            preprocessor = load_obj(path=self.artifact.transformed_object_file_path)
            logging.info("Preprocessor object loaded successfully")

            logging.info("Tracking the best model, params and metrics in MLflow")
            self.track_model(
                best_model,
                classification_train_metric.__dict__,
                classification_test_metric.__dict__,
                best_params
            )

            model_dir_path = os.path.dirname(self.config.model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)  # FIX: exist_ok=True, інакше впаде при повторному запуску
            logging.info(f"Model directory ensured at {model_dir_path}")

            full_model = NetworkModel(preprocess=preprocessor, model=best_model)
            save_obj(full_model, "final_model/full_model.pkl")  # FIX: порядок аргументів (file_path, obj)
            logging.info(f"Full model (preprocessor+model) saved at {self.config.model_file_path}")

            save_obj(best_model, "final_model/model.pkl")  # FIX: порядок аргументів (file_path, obj)
            logging.info("Best raw model saved at final_model/model.pkl")

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.config.model_file_path,  # FIX: self.model_trainer_config не існує
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )
            logging.info(f"Model trainer artifact created: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"Error during model training: {e}")
            raise NetworkSecurityException(e, sys)

    def init_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logging.info("Initiating model trainer pipeline")

            train_file_path = self.artifact.transformed_train_file_path  # FIX: self.data_transformation_artifact не існує
            test_file_path = self.artifact.transformed_test_file_path

            train_arr = load_numpy_array(train_file_path)
            test_arr = load_numpy_array(test_file_path)
            logging.info("Loaded train and test numpy arrays")

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )
            logging.info(f"Split data: X_train={x_train.shape}, X_test={x_test.shape}")

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            logging.info("Model trainer pipeline completed successfully")
            return model_trainer_artifact

        except Exception as e:
            logging.error(f"Error in init_model_trainer: {e}")
            raise NetworkSecurityException(e, sys)