from sklearn.metrics import f1_score, recall_score, precision_score
from networksecurity.entity.artifact_entity import ClassificationMetricReport
import sys
from networksecurity.exceptions.exception import NetworkSecurityException
def get_classification_scores(y_pred, y_true)->ClassificationMetricReport:
    try:
        model_f1_score = f1_score(y_true, y_pred)
        model_recall_score = recall_score(y_true, y_pred)
        model_precision_score=precision_score(y_true,y_pred)
    
        report_obj = ClassificationMetricReport(
            f1_score= model_f1_score,
            recall_score= model_recall_score,
            precision_score= model_precision_score
        )
        return report_obj
    except Exception as e:
        raise NetworkSecurityException(e, sys)