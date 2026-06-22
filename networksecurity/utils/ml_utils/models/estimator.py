from networksecurity.exceptions.exception import NetworkSecurityException
import os, sys
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
class NetworkModel:
    def __init__(self, model, preprocess):
        try:
            self.model = model
            self.preprocess = preprocess
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def predict(self, data):
        try:
            preprocess_data = self.preprocess.transform(data)
            return self.model.predict(preprocess_data)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

def evaluate_models(X_train, y_train, X_test, y_test, models, params):
    try:
        report = {}

        for model_name, model in models.items():
            para = params[model_name]

            gs = GridSearchCV(model, para, cv=3, n_jobs=-1)
            gs.fit(X_train, y_train)

            best_model = gs.best_estimator_

            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)

            train_model_score = r2_score(y_train, y_train_pred)
            test_model_score = r2_score(y_test, y_test_pred)

            report[model_name] = {
                "model": best_model,
                "best_params": gs.best_params_,
                "train_score": train_model_score,
                "test_score": test_model_score,
            }

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)