
import boto3
import time
import os

def extract_plain_text_from_pdf_async(document):

    profile = os.environ.get("AWS_PROFILE", "default")
    session = boto3.Session(profile_name=profile)
    client = session.client('textract')
    bucket = "extract-value"

    # Start asynchronous document analysis
    response = client.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': document}},
        FeatureTypes=["TABLES", "FORMS"]
    )
    job_id = response['JobId']
    print(f"Started Textract job with JobId: {job_id}")

    # Wait for the job to complete
    while True:
        result = client.get_document_analysis(JobId=job_id)
        status = result['JobStatus']
        print(f"Job status: {status}")
        if status in ["SUCCEEDED", "FAILED"]:
            break
        time.sleep(5)

    if status == "FAILED":
        print("Textract job failed.")
        return None

    # Collect all pages (pagination)
    blocks = []
    next_token = result.get('NextToken', None)
    blocks.extend(result['Blocks'])
    while next_token:
        result = client.get_document_analysis(JobId=job_id, NextToken=next_token)
        blocks.extend(result['Blocks'])
        next_token = result.get('NextToken', None)

    # Extract lines
    # lines = []
    # for block in blocks:
    #     if block['BlockType'] == 'LINE':
    #         lines.append(block['Text'])
    # plain_text = '\n'.join(lines)

    import json
    lines = []
    for block in blocks:
        if block['BlockType'] == 'LINE':
            lines.append({
                "Id": block['Id'],
                "Text": block['Text'],
                "Geometry": block['Geometry'],
                "Page": block['Page'],
                "Confidence": block['Confidence']
            })
            
    return lines

def main():
    document = "fayet_bail_commercial.pdf"
    extract_plain_text_from_pdf_async(document)

if __name__ == "__main__":
    main()
