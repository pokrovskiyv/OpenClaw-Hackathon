#!/usr/bin/env python3
import json
import subprocess

def get_all_pr_comments(owner, repo, pr_number, token):
    """Получить ВСЕ комментарии к PR с пагинацией"""
    all_comments = []
    page = 1
    per_page = 100
    
    while True:
        result = subprocess.run([
            'curl', '-s',
            '-H', f'Authorization: Bearer {token}',
            f'https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments?per_page={per_page}&page={page}'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            break
        
        try:
            comments = json.loads(result.stdout)
            if isinstance(comments, list):
                all_comments.extend(comments)
                if len(comments) < per_page:
                    break  # Последняя страница
                page += 1
            else:
                break
        except:
            break
    
    return all_comments

def analyze_comment(comment_body):
    """Анализировать комментарий - полезный или нет"""
    lower_body = comment_body.lower()
    
    # Полезные комментарии
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
        'major', 'critical', 'issue',
        'minor', 'warning', 'potential'
    ]
    
    # Неполезные комментарии
    not_useful_patterns = [
        'good job', 'nice', 'отлично', 'молодец',
        'thanks', 'спасибо', 'thank you',
        'merge when ready', 'ready to merge',
        'approve', '+1', 'lgtm', 'look good',
        'walkthrough',
        'finishing touches'
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
    
    # Получаем ВСЕ комментарии
    comments = get_all_pr_comments(owner, repo, pr_number, token)
    
    if not comments:
        return "✅ Нет комментариев в PR"
    
    # Анализируем
    useful_comments = []
    
    for comment in comments:
        if isinstance(comment, dict) and comment.get('body'):
            is_useful, reason = analyze_comment(comment['body'])
            if is_useful:
                user = comment.get('user', {}).get('login', 'Unknown')
                # Обрезаем очень длинные комментарии
                body = comment['body'][:150] + '...' if len(comment['body']) > 150 else comment['body']
                useful_comments.append({
                    'user': user,
                    'body': body,
                    'reason': reason
                })
    
    # Формируем отчёт
    summary = f"📊 Проверка PR #{pr_number}\n\n"
    
    if useful_comments:
        summary += f"⚠️ Полезных комментариев: {len(useful_comments)}\n\n"
        for comment in useful_comments[:3]:
            summary += f"• @{comment['user']}: {comment['body']}\n"
        if len(useful_comments) > 3:
            summary += f"  ... и ещё {len(useful_comments) - 3}\n"
        
        summary += f"\n⚡ Действия:"
        summary += f"\n• Если критично → исправь и закрой"
        summary += f"\n• Если не критично → просто закрой"
    else:
        summary += "✅ Нет требуемых исправлений"
    
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
