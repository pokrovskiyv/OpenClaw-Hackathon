#!/usr/bin/env python3
import json
import subprocess

def get_pr_comments(owner, repo, pr_number, token):
    """Получить ВСЕ комментарии к PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

def get_pr_commits(owner, repo, pr_number, token):
    """Получить все коммиты в PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

def analyze_comment(comment_body):
    """Анализировать комментарий - полезный или нет, и тип"""
    lower_body = comment_body.lower()
    
    # Полезные комментарии (требуют исправлений)
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
    
    # Неполезные комментарии (просто информационные)
    not_useful_patterns = [
        'good job', 'nice', 'отлично', 'молодец',
        'thanks', 'спасибо', 'thank you',
        'merge when ready', 'ready to merge',
        'approve', '+1', 'lgtm', 'look good',
        'walkthrough', 'finishing touches'
    ]
    
    # Предупреждения (важные, но не обязательно требуют исправлений)
    warning_patterns = [
        'rate limit', 'warning', 'potential',
        'pre-merge', 'walkthrough'
    ]
    
    for pattern in useful_patterns:
        if pattern in lower_body:
            return (True, "requires_fix", "useful")
    
    for pattern in not_useful_patterns:
        if pattern in lower_body:
            return (False, "resolved", "not_useful")
    
    for pattern in warning_patterns:
        if pattern in lower_body:
            return (True, "requires_fix", "warning")
    
    return (False, "resolved", "unprocessed")

def resolve_comment(owner, repo, issue_number, comment_id, token, state="resolved"):
    """Отметить комментарий как resolved"""
    result = subprocess.run([
        'curl', '-X', 'PATCH',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        '-H', 'Content-Type: application/json',
        '-d', f'{{"state": "{state}"}}'
    ], capture_output=True, text=True)
    
    return result.returncode == 0

def classify_comments(comments):
    """Классифицировать комментарии по типу"""
    classified = {
        'useful': [],
        'warnings': [],
        'resolved': []
    }
    
    for comment in comments:
        if not isinstance(comment, dict) or not comment.get('body'):
            continue
            
        is_useful, comment_type, _ = analyze_comment(comment['body'])
        
        if comment_type == "useful":
            classified['useful'].append(comment)
        elif comment_type == "warning":
            classified['warnings'].append(comment)
        elif comment_type == "resolved":
            classified['resolved'].append(comment)
    
    return classified

def check_pr(owner, repo, pr_number, token):
    """Проверить PR и вернуть отчёт"""
    
    # Получаем все комментарии
    comments = get_pr_comments(owner, repo, pr_number, token)
    
    if not comments:
        return "✅ Нет комментариев в PR"
    
    # Классифицируем
    classified = classify_comments(comments)
    
    # Формируем отчёт
    summary = f"📊 Проверка PR #{pr_number}\n"
    summary += f"📝 Всего комментариев: {len(comments)}\n\n"
    
    # Полезные (требуют исправлений)
    if classified['useful']:
        summary += f"⚠️ Требуют исправлений: {len(classified['useful'])}\n\n"
        for i, comment in enumerate(classified['useful'][:3]):
            user = comment.get('user', {}).get('login', 'Unknown')
            body = comment['body'][:120]
            summary += f"{i}. @{user}: {body}...\n"
        if len(classified['useful']) > 3:
            summary += f"   ... и ещё {len(classified['useful']) - 3}\n"
    
    # Предупреждения
    if classified['warnings']:
        summary += f"⚡ Предупреждения: {len(classified['warnings'])} (информационные, не требуют исправлений)\n\n"
        for i, comment in enumerate(classified['warnings'][:2]):
            user = comment.get('user', {}).get('login', 'Unknown')
            body = comment['body'][:80]
            summary += f"{i}. @{user}: {body}...\n"
    
    # Действия
    if classified['useful'] or classified['warnings']:
        summary += f"\n⚡ Действия:\n"
        summary += "• Для предупреждений и неважных → можно оставить без действий\n"
        summary += "• Для полезных комментариев → нужно исправить и закоммитить\n"
        summary += "• После исправлений → PR готов к merge\n"
    else:
        summary += "✅ Нет требуемых исправлений\n"
    
    # Уведомления о разрешённых комментариях
    if classified['resolved']:
        summary += f"\nℹ️ Отмечено как resolved: {len(classified['resolved'])} комментариев (информационные)\n"
        for comment in classified['resolved'][:2]:
            user = comment.get('user', {}).get('login', 'Unknown')
            summary += f"   @{user}\n"
    
    return summary

if __name__ == "__main__":
    import sys
    
    try:
        with open('/root/.openclaw/credentials/.gh_token', 'r') as f:
            token = f.read().strip()
    except:
        print("❌ GitHub token not found")
        sys.exit(1)
    
    owner = "pokrovskiyv"
    repo = "OpenClaw-Hackathon"
    pr_number = sys.argv[1] if len(sys.argv) > 1 else 2
    
    summary = check_pr(owner, repo, pr_number, token)
    print(summary)
