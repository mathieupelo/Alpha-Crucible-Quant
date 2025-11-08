"""
Shared utilities for repository execution DAGs.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

# Base directory for cloned repos
REPOS_BASE_DIR = Path('/opt/airflow/repos')


def clone_or_update_repo(repo_config: Dict) -> str:
    """Clone or update a repository."""
    repo_name = repo_config['name']
    repo_url = repo_config['url']
    repo_path = REPOS_BASE_DIR / repo_name
    
    try:
        if repo_path.exists():
            logger.info(f"Updating existing repository: {repo_name}")
            # Update existing repo
            result = subprocess.run(
                ['git', 'pull'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Updated {repo_name}: {result.stdout}")
        else:
            logger.info(f"Cloning new repository: {repo_name}")
            # Clone new repo
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ['git', 'clone', repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Cloned {repo_name}: {result.stdout}")
        
        return str(repo_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning/updating {repo_name}: {e.stderr}")
        raise


def build_docker_image(repo_path: str, repo_name: str) -> bool:
    """Build Docker image for a repository."""
    try:
        logger.info(f"Building Docker image for {repo_name}")
        
        # Check for Dockerfile or Dockerfile.txt
        dockerfile_path = Path(repo_path) / 'Dockerfile'
        dockerfile_txt_path = Path(repo_path) / 'Dockerfile.txt'
        
        build_cmd = ['docker', 'build', '-t', f'{repo_name}:latest']
        
        # Use Dockerfile.txt if Dockerfile doesn't exist
        if not dockerfile_path.exists() and dockerfile_txt_path.exists():
            logger.info(f"Using Dockerfile.txt (Dockerfile not found)")
            build_cmd.extend(['-f', 'Dockerfile.txt'])
        
        build_cmd.append('.')
        
        result = subprocess.run(
            build_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Built Docker image for {repo_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building Docker image for {repo_name}: {e.stderr}")
        raise


def run_repo_container(repo_config: Dict, repo_path: str) -> int:
    """Run a repository container with environment variables."""
    repo_name = repo_config['name']
    
    # Prepare environment variables
    env_vars = {
        'ORE_DATABASE_URL': os.getenv('ORE_DATABASE_URL', ''),
        'ORE_DB_HOST': os.getenv('ORE_DB_HOST', ''),
        'ORE_DB_PORT': os.getenv('ORE_DB_PORT', '5432'),
        'ORE_DB_USER': os.getenv('ORE_DB_USER', ''),
        'ORE_DB_PASSWORD': os.getenv('ORE_DB_PASSWORD', ''),
        'ORE_DB_NAME': os.getenv('ORE_DB_NAME', ''),
        'DATABASE_URL': os.getenv('DATABASE_URL', ''),
        'DB_HOST': os.getenv('DB_HOST', ''),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_USER': os.getenv('DB_USER', ''),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
        'DB_NAME': os.getenv('DB_NAME', ''),
        # Reddit API credentials
        'DATABASE_ORE_URL': os.getenv('DATABASE_ORE_URL', ''),
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID', ''),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET', ''),
        'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT', ''),
    }
    
    # Add PYTHONPATH if workdir is specified in repo_config (for module imports)
    if 'workdir' in repo_config:
        env_vars['PYTHONPATH'] = repo_config['workdir']
    
    # Build env list for docker run
    env_list = []
    for key, value in env_vars.items():
        if value:  # Only add non-empty values
            env_list.extend(['-e', f'{key}={value}'])
    
    try:
        logger.info(f"Running Docker container for {repo_name}")
        
        # Build docker run command
        cmd = [
            'docker', 'run', '--rm',
            *env_list,
            f'{repo_name}:latest'
        ]
        
        # If custom command is specified, append it (overrides CMD in Dockerfile)
        if 'command' in repo_config:
            custom_cmd = repo_config['command']
            if isinstance(custom_cmd, list):
                cmd.extend(custom_cmd)
            else:
                cmd.append(custom_cmd)
            logger.info(f"Using custom command: {' '.join(custom_cmd) if isinstance(custom_cmd, list) else custom_cmd}")
        
        # Set working directory if specified (for module imports)
        if 'workdir' in repo_config:
            # Insert workdir flag before the image name
            workdir_idx = cmd.index(f'{repo_name}:latest')
            cmd.insert(workdir_idx, '-w')
            cmd.insert(workdir_idx + 1, repo_config['workdir'])
            logger.info(f"Setting working directory to: {repo_config['workdir']}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Container {repo_name} completed successfully")
        logger.info(f"Output: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"Stderr: {result.stderr}")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Container {repo_name} failed with exit code {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Stdout: {e.stdout}")
        raise


def execute_repo_task(repo_config: Dict, **context):
    """Execute a single repository task."""
    repo_name = repo_config['name']
    
    try:
        # Step 1: Clone or update repo
        repo_path = clone_or_update_repo(repo_config)
        
        # Step 2: Build Docker image
        build_docker_image(repo_path, repo_name)
        
        # Step 3: Run container
        exit_code = run_repo_container(repo_config, repo_path)
        
        if exit_code != 0:
            raise Exception(f"Repository {repo_name} exited with code {exit_code}")
        
        logger.info(f"Successfully executed {repo_name}")
        return f"Success: {repo_name}"
        
    except Exception as e:
        logger.error(f"Failed to execute {repo_name}: {e}")
        raise

