FROM python:3.7

RUN pip install -U pip boto3 sagemaker pandas numpy s3fs sklearn

WORKDIR /root/workspace
ADD train.py train.py
CMD ["python", "train.py"]