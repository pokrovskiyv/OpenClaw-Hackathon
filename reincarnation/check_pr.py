#!/usr/bin/env python3
import json
import time
import subprocess
from datetime import datetime, timedelta

def get_pr_comments(owner, repo, pr_number, token):
    """Получить комментарии к PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else []
    return []

def get_pr_reviews(owner, repo, pr_number, token):
    """Получить review comments к PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data if isinstance(data, list) else []
    return []

def get_pr_status(owner, repo, pr_number, token):
    """Получить статус PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def analyze_comment(comment_body):
    """Анализировать комментарий - полезный или нет"""
    lower_body = comment_body.lower()
    
    # Полезные комментарии
    useful_patterns = [
        'bug', 'error', 'fix', 'incorrect', 'wrong',
        'проблема', 'ошибка', 'исправить', 'неправильно',
        'typo', 'мелочь', 'опечатка',
        'suggest', 'рекомендую', 'предлагаю',
        'improve', 'улучшить',
        'security', 'безопасность',
        'performance', 'производительность',
        'documentation', 'документация'
    ]
    
    # Неполезные комментарии
    not_useful_patterns = [
        'good job', 'nice', 'отлично', 'молодец',
        'thanks', 'спасибо', 'thank you',
        'merge when ready', 'ready to merge',
        'approve', '+1', 'lgtm', 'look good'
    ]
    
    for pattern in useful_patterns:
        if pattern in lower_body:
            return (True, "Requires fix")
    
    for pattern in not_useful_patterns:
        if pattern in lower_body:
            return (False, "Just feedback")
    
    return (True, "Potentially useful")

def check_pr(owner, repo, pr_number, token):
    """Проверить PR и вернуть отчёт"""
    
    # Получаем статус PR
    pr_status = get_pr_status(owner, repo, pr_number, token)
    if not pr_status:
        return "❌ Не удалось получить статус PR"
    
    if pr_status.get('state') == 'closed':
        return "✅ PR уже закрыт"
    
    # Получаем комментарии
    comments = get_pr_comments(owner, repo, pr_number, token)
    reviews = get_pr_reviews(owner, repo, pr_number, token)
    
    # Объединяем комментарии
    all_comments = []
    
    for comment in comments:
        if isinstance(comment, dict):
            all_comments.append({
                'id': str(comment.get('id', '')),
                'body': comment.get('body', ''),
                'user': comment.get('user', {}).get('login', 'Unknown'),
                'type': 'comment'
            })
    
    for review in reviews:
        if isinstance(review, dict):
            body = review.get('body', '')
            if body:
                all_comments.append({
                    'id': str(review.get('id', '')),
                    'body': body,
                    'user': review.get('user', {}).get('login', 'Unknown'),
                    'type': 'review'
                })
    
    if not all_comments:
        return "✅ Нет комментариев в PR"
    
    # Анализируем
    useful_comments = []
    not_useful_comments = []
    
    for comment in all_comments:
        is_useful, reason = analyze_comment(comment['body'])
        if is_useful:
            useful_comments.append({
                'user': comment['user'],
                'body': comment['body'][:80]
            })
        else:
            not_useful_comments.append({
                'user': comment['user'],
                'body': comment['body'][:80]
            })
    
    # Формируем отчёт
    summary = f"📊 Проверка PR #{pr_number}\n\n"
    
    if useful_comments:
        summary += f"⚠️ Полезные комментарии: {len(useful_comments)}\n\n"
        for comment in useful_comments[:2]:
            summary += f"• @{comment['user']}: {comment['body']}...\n"
    else:
        summary += "✅ Нет требуемых исправлений\n"
    
    if not_useful_comments:
        summary += f"\n✓ Обычные отзывы: {len(not_useful_comments)}\n"
    
    if useful_comments:
        summary += f"\n⚡ Действия:"
        summary += f"\n• Если критично → исправь и закрой"
        summary += f"\n• Если не критично → просто закрой"
    
    return summary

if __name__ == "__main__":
    import sys
    
    # Получаем токен
    try:
        with open('/root/.openclaw/credentials/.gh_token', 'r') as f:
            token = f.read().strip()
    except:
        print("❌ GitHub token not found")
        sys.exit(1)
    
    # Параметры
    owner = "pokrovskiyv"
    repo = "OpenClaw-Hackathon"
    pr_number = 2
    
    summary = check_pr(owner, repo, pr_number, token)
    print(summary)
