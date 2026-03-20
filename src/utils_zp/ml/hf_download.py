import subprocess
import sys

def hf_download(repo, local_dir, retry_times: int = 3):
    """
    Download a Hugging Face repository to a local directory using subprocess.
    
    Args:
        repo (str): Hugging Face repository name (e.g., "bert-base-uncased")
        local_dir (str): Local directory path to save the model
        retry_times (int): Number of retry attempts if download fails
    
    Returns:
        bool: True if download successful, False if all retries failed
    
    Raises:
        subprocess.TimeoutExpired: If the download process times out
    """
    
    # Ensure huggingface-hub is installed
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "show", "huggingface-hub"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("huggingface-hub not found. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface-hub"],
            check=True
        )
    
    # Build the command
    cmd = [
        'hf',
        "download",
        repo,
        "--local-dir", local_dir,
        # "--resume-download",
    ]
    
    # Try download with retries
    for attempt in range(retry_times):
        try:
            print(f"Download attempt {attempt + 1}/{retry_times} for {repo} to {local_dir}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=3600  # 1 hour timeout
            )
            
            print(f"Successfully downloaded {repo}")
            if result.stdout:
                print(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Download failed on attempt {attempt + 1}: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            
            if attempt == retry_times - 1:
                print(f"All {retry_times} attempts failed for {repo}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Download timeout on attempt {attempt + 1}")
            if attempt == retry_times - 1:
                print(f"All {retry_times} attempts timed out for {repo}")
                return False
                
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == retry_times - 1:
                return False

