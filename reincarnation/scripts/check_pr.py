#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.error
from urllib.parse import urlencode

# Константы
GITHUB_API_BASE = "https://api.github.com/repos/"
DEFAULT_OWNER = "pokrovskiyv"
DEFAULT_REPO = "OpenClaw-Hackathon"
DEFAULT_PR_NUMBER = 2

def get_github_token():
    """Получить GitHub токен из env или файла"""
    token_path = os.getenv("GH_TOKEN_PATH", "/root/.openclaw/credentials/.gh_token")
    token = os.getenv("GH_TOKEN")
    
    if token:
        return token.strip()
    
    try:
        with open(token_path, 'r') as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError) as e:
        print(f"❌ GitHub token not found: {e}", file=sys.stderr)
        sys.exit(1)

def make_github_request(url, token, timeout=30):
    """Сделать HTTP запрос к GitHub API с urllib"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'OpenClaw-Agent'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP error {e.code}: {e.reason}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"❌ URL error: {e.reason}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return []

def get_pr_comments(owner, repo, pr_number, token):
    """Получить ВСЕ комментарии к PR с пагинацией"""
    url = f"{GITHUB_API_BASE}{owner}/{repo}/pulls/{pr_number}/comments"
    all_comments = []
    page = 1
    per_page = 100
    max_pages = 10  # Защита от бесконечной пагинации
    
    while page <= max_pages:
        params = urlencode({'page': page, 'per_page': per_page})
        full_url = f"{url}?{params}"
        
        comments = make_github_request(full_url, token)
        
        if not comments or not isinstance(comments, list):
            break
        
        all_comments.extend(comments)
        
        if len(comments) < per_page:
            break  # Последняя страница
        
        page += 1
    
    return all_comments

def analyze_comment(comment_body):
    """Анализировать комментарий - полезный или нет"""
    lower_body = comment_body.lower()
    
    useful_patterns = [
        'bug', 'error', 'fix', 'incorrect', 'wrong',
        'проблема', 'ошибка', 'исправить', 'неправильно',
        'typo', 'опечатка',
        'suggest', 'рекомендую', 'предлагаю',
        'improve', 'улучшить',
        'security', 'безопасность',
        'performance', 'производительность',
        'documentation', 'документация',
        'outdated', 'устаревший',
        'major', 'critical', 'issue'
    ]
    
    not_useful_patterns = [
        'good job', 'nice', 'отлично', 'молодец',
        'thanks', 'спасибо', 'thank you',
        'merge when ready', 'ready to merge',
        'approve', '+1', 'lgtm', 'look good',
        'walkthrough', 'finishing touches'
    ]
    
    for pattern in useful_patterns:
        if pattern in lower_body:
            return (True, "requires_fix")
    
    for pattern in not_useful_patterns:
        if pattern in lower_body:
            return (False, "resolved")
    
    return (False, "unprocessed")

def check_pr(owner, repo, pr_number, token):
    """Проверить PR и вернуть отчёт"""
    comments = get_pr_comments(owner, repo, pr_number, token)
    
    if not comments:
        return "✅ Нет комментариев в PR"
    
    useful_comments = []
    for comment in comments:
        if isinstance(comment, dict) and comment.get('body'):
            is_useful, status = analyze_comment(comment['body'])
            if is_useful:
                user = comment.get('user', {}).get('login', 'Unknown')
                body = comment['body'][:150]
                useful_comments.append({'user': user, 'body': body})
    
    if useful_comments:
        summary = f"📊 Проверка PR #{pr_number}\n\n"
        summary += f"⚠️ Требуют исправлений: {len(useful_comments)}\n\n"
        for i, comment in enumerate(useful_comments[:3]):
            summary += f"{i}. @{comment['user']}: {comment['body']}\n"
        if len(useful_comments) > 3:
            summary += f"   ... и ещё {len(useful_comments) - 3}\n"
        return summary
    
    return "✅ Нет требуемых исправлений"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check PR for comments')
    parser.add_argument('--owner', default=os.getenv('PR_OWNER', DEFAULT_OWNER))
    parser.add_argument('--repo', default=os.getenv('PR_REPO', DEFAULT_REPO))
    parser.add_argument('--pr-number', type=int, default=int(os.getenv('PR_NUMBER', DEFAULT_PR_NUMBER)))
    args = parser.parse_args()
    
    token = get_github_token()
    summary = check_pr(args.owner, args.repo, args.pr_number, token)
    print(summary)
