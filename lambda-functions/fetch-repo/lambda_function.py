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
            github_token = os.environ.get('GITHUB_TOKEN')

            if github_token:
                headers['Authorization'] = f'token {github_token}'

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                tree_data = response.json()
                print(f"Found branch: {branch}")
                break


        ## Error handling
        if not tree_data:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Repository not found or no main/master branch',
                    'status_code': response.status_code
                })
            }


        ## process files
        tree = tree_data.get('tree', [])
        files_processed = 0
        files_skipped = 0

        for item in tree:
            if item['type'] != 'blob':
                continue

            file_path = item['path']


            # skip unnecessary files
            if should_skip_file(file_path):
                files_skipped += 1
                continue

            # download file
            try:
                file_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_path}"
                file_response = requests.get(file_url, timeout=10)

                # try master if there is no main
                if file_response.status_code != 200:
                    file_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{file_path}"
                    file_response = requests.get(file_url, timeout=10)


                # S3
                if file_response.status_code == 200:
                    s3_key = f"{repo_id}/{file_path}"  

                s3.put_object(
                    Bucket = BUCKET_NAME,
                    Key = s3_key,
                    Body = file_response.content,
                    ContentType = get_content_type(file_path)
                )


                files_processed += 1

                if files_processed % 10 == 0:
                    print(f"Processed {files_processed} files...")  

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue


        print(f'Complete! Processed: {files_processed}, Skipped: {files_skipped}')


        return {
            'statusCode' : 200,
            'body' : json.dumps({
                'repoId': repo_id,
                'filesProcessed' : files_processed,
                'filesSkipped' : files_skipped,
                'bucket' : BUCKET_NAME
            })
        }


    
    except Exception as e:
        print(f'Error: str({e})')
        return {
            'statusCode' : 500,
            'body' : json.dumps({'error' : str(e) })

        }
        
## other functions
def should_skip_file(file_path):
    """
        Skip unnecessary files
    """

    skip_patterns = [
        # env
        'node_modules/', 'vendor/', 'venv/', '__pycache__/',
        
        # Version control
        '.git/', '.svn/',
        
        # IDE
        '.vscode/', '.idea/',
        
        # Binary/Media
        '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip',
        '.mp3', '.mp4', '.exe', '.dll',
        
        # Lock files
        'package-lock.json', 'yarn.lock'
    ]

    file_lower = file_path.lower()
    return any(pattern in file_lower for pattern in skip_patterns)

def get_content_type(file_path):
    """
        Defime MIME type according to file
    """

    extension = file_path.split('.')[-1].lower()

    content_types = {
        'js': 'application/javascript',
        'py': 'text/x-python',
        'java': 'text/x-java',
        'json': 'application/json',
        'html': 'text/html',
        'css': 'text/css',
        'md': 'text/markdown',
        'txt': 'text/plain', 
    }

    return content_types.get(extension, 'text/plain')
