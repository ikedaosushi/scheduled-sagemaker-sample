import os

import pandas as pd
from sklearn.model_selection import train_test_split
import boto3
import sagemaker
from sagemaker.predictor import csv_serializer
from sagemaker.session import s3_input

S3_BUCKET = os.environ['S3_BUCKET']
SM_ROLE =  os.environ['SM_ROLE']
REGION_NAME = os.environ['REGION_NAME']

VAL_SIZE = os.environ.get("VAL_SIZE", 0.2)
RANDOM_STATE = os.environ.get("RANDOM_STATE", 42)

TRAIN_IMAGE_NAME = os.environ.get("TRAIN_IMAGE_NAME", '501404015308.dkr.ecr.ap-northeast-1.amazonaws.com/xgboost:latest')
TRAIN_INSTANCE_TYPE = os.environ.get("TRAIN_INSTANCE_TYPE", 'ml.m4.xlarge')
TRAIN_INSTANCE_COUNT = os.environ.get("TRAIN_INSTANCE_COUNT", 1)

DEPLOY_INSTANCE_TYPE = os.environ.get("DEPLOY_INSTANCE_TYPE", 'ml.t2.medium')
DEPLOY_INSTANCE_COUNT = os.environ.get("DEPLOY_INSTANCE_COUNT", 1)
DEPLOY_ENDPOINT_NAME = os.environ.get("DEPLOY_ENDPOINT_NAME", 'dx-materials')

S3_INPUT_PATH = f"s3://{S3_BUCKET}/inputs/raw/data.csv"
S3_TRAIN_PATH = f"s3://{S3_BUCKET}/inputs/train/train.csv"
S3_VALID_PATH = f"s3://{S3_BUCKET}/inputs/validation/validation.csv"
S3_OUTPUT_PATH = f"s3://{S3_BUCKET}/output"

def preprocess():
    # load
    df = pd.read_csv(S3_INPUT_PATH)
    # transform
    y_col = 'material'
    x_cols = [c for c in df.columns if c != y_col]
    df = df[[y_col] + x_cols]
    # split
    train_data, val_data = train_test_split(df, test_size=(VAL_SIZE), random_state=RANDOM_STATE)
    # upload
    train_data.to_csv(S3_TRAIN_PATH, header=False, index=False)
    val_data.to_csv(S3_VALID_PATH, header=False, index=False)

def train():
    boto_session = boto3.Session(region_name=REGION_NAME)
    sagemaker_session = sagemaker.Session(boto_session=boto_session)
    xgb = sagemaker.estimator.Estimator(
        image_name=TRAIN_IMAGE_NAME,
        role=SM_ROLE,
        train_instance_count=TRAIN_INSTANCE_COUNT,
        train_instance_type=TRAIN_INSTANCE_TYPE,
        output_path=S3_OUTPUT_PATH,
        sagemaker_session=sagemaker_session
    )

    # train
    train_params = {
        "eta": 0.1,
        "objective": 'multi:softprob',
        "num_class": 4,
        "eval_metric": 'mlogloss',
        "num_round":100
    }
    xgb.set_hyperparameters(**train_params)
    xgb.fit({
        'train': s3_input(s3_data=S3_TRAIN_PATH, content_type="csv"),
        'validation': s3_input(s3_data=S3_VALID_PATH, content_type="csv")
    })
    # deploy
    deploy_params = {
        "initial_instance_count": DEPLOY_INSTANCE_COUNT,
        "instance_type": DEPLOY_INSTANCE_TYPE,
        "endpoint_name": DEPLOY_ENDPOINT_NAME,
        "update_endpoint": True
    }
    xgb.deploy(**deploy_params)

if __name__ == "__main__":
    preprocess()
    train()