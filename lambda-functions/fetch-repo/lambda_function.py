import json
import boto3
import os
import requests
from urllib.parse import urlparse ## to parse repository URL

## create s3 connection
s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'codeonboard-ai-repos')

## main function
def lambda_handler(event, context):

    """
    Download code files from github repo and store in S3 
    
    Input: {"githubUrl": "https://github.com/owner/repo"}
    Output: {"statusCode": 200, "body": {...}}
    """

    try:
        github_url = event.get('githubUrl')

        if not github_url:
            return {
                'statusCode' : 400,
                'body' : json.dumps({'error': 'Missing githubUrl parameter'})

            }
        
        ## parse repo and owner names
        ## example url: https://github.com/cansumericli/codeonboard-ai

        parts = github_url.strip('/').split('/')

        if len(parts) < 2 :
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid GitHub URL format'})
            }
        
        repo = parts[-1]
        owner = parts[-2]

        repo_id = f"{owner}_{repo}"

        print(f"Fetching repository : {owner}/{repo}")


        ## Github api : pull files in the repo
        ## try main branch first, if not found then iterate master

        ##example url: https://github.com/cansumericli/s3-object-ingestion-catalog/tree/main/src/ingest

        tree_data = None

        for branch in ['main', 'master']: ## master for old repos
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

            headers = {}
            github_token = os.environment.get('GITHUB_TOKEN')

            if github_token:
                headers['Authorization'] = f'token {github_token}'

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                tree_data = response.json()
                print(f"Found branch: {branch}")
                break


        ## Error
        if not tree_data:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Repository not found or no main/master branch',
                    'status_code': response.status_code
                })
            }






    
    except Exception as e:
        print(f'Error: str({e})')
        return {
            'statusCode' : 500,
            'body' : json.dumps({'error' : str(e) })

        }
        
        