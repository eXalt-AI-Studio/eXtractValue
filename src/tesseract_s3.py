
import boto3
import time

def extract_plain_text_from_pdf_async(document):

    session = boto3.Session(profile_name="AdministratorAccess-004843573718")
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
    lines = []
    for block in blocks:
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
    plain_text = '\n'.join(lines)
    print('--- Extracted Plain Text ---')
    print(plain_text)
    return plain_text

def main():
    document = "fayet_bail_commercial.pdf"
    extract_plain_text_from_pdf_async(document)

if __name__ == "__main__":
    main()
