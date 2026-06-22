from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.exceptions.exception import NetworkSecurityException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from networksecurity.utils.main_utils.utils import load_obj
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
import pymongo
import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URI_CONNECT")

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constants.training_pipeline import  DATA_INGESTION_DB_NAME

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates("./templates")

database = client[DATA_INGESTION_DB_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        df = df.drop(columns="Result")
        full_model = load_obj("final_model/full_model.pkl")
        y_pred = full_model.predict(df)
        df['predicted_column'] = y_pred
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys)
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)