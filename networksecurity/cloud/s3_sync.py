import boto3
from pathlib import Path

from pathlib import Path
import boto3

s3_client = boto3.client('s3')

def artifact_to_s3(artifact_path, bucket, folder):
    
    artifact_path = Path(artifact_path)
    
    for path, dirs, files in artifact_path.walk():
        for file in files:
            local_file_path = path / file

            relative_path = local_file_path.relative_to(artifact_path)

            s3_key = f"{folder.strip('/')}/{relative_path.as_posix()}"
            
            print(f"Завантаження: {local_file_path} -> s3://{bucket}/{s3_key}")
            
            s3_client.upload_file(
                Filename=str(local_file_path), 
                Bucket=bucket,                  
                Key=s3_key                      
            )
            

def model_to_s3(path, bucket, folder):
    path = Path(path)
    s3_key = f"{folder.strip('/')}/{path.as_posix()}"
    
    s3_client.upload_file(
        Filename=str(path), 
        Bucket=bucket,                  
        Key=s3_key                      
    )
            
def s3_to_artifact(artifact_path, bucket, folder):
    local_base = Path(artifact_path)
    
    prefix = f"{folder.strip('/')}/"
    
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if 'Contents' not in response:
        print(f"Папка {folder} порожня або не існує в бакеті {bucket}.")
        return

    for obj in response['Contents']:
        s3_key = obj['Key']
        
        if s3_key.endswith('/'):
            continue

        relative_path = Path(s3_key).relative_to(folder)
        local_file_path = local_base / relative_path
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Скачування: s3://{bucket}/{s3_key} -> {local_file_path}")
        s3_client.download_file(
            Bucket=bucket,
            Key=s3_key,
            Filename=str(local_file_path)
        )
        
    