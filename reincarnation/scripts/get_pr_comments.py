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
        try:
            return try:
        json.loads(result.stdout)
    except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
        print(f"JSON parsing error: {e}", file=sys.stderr)
        return {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return []
    return []

def get_pr_commits(owner, repo, pr_number, token):
    """Получить все коммиты в PR"""
    result = subprocess.run([
        'curl', '-s',
        '-H', f'Authorization: Bearer {token}',
        f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            return try:
        json.loads(result.stdout)
    except (json.JSONDecodeError, OSError, KeyError, ValueError) as e:
        print(f"JSON parsing error: {e}", file=sys.stderr)
        return {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return []
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
    
    # Предупреждения (информационные, не требуют исправлений)
    warning_patterns = [
        'rate limit', 'warning', 'potential',
        'pre-merge'
    ]
    
    # Неполезные (просто информационные)
    not_useful_patterns = [
        'good job', 'nice', 'отлично', 'молодец',
        'thanks', 'спасибо', 'thank you',
        'merge when ready', 'ready to merge',
        'approve', '+1', 'lgtm', 'look good',
        'walkthrough', 'finishing touches',
        'summarize', 'summary',
        'rate limited',
        'exceeded'
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
    
    return (False, "unprocessed", "unknown")

def check_pr(owner, repo, pr_number, token):
    """Проверить PR и вернуть отчёт"""
    
    # Получаем все комментарии
    comments = get_pr_comments(owner, repo, pr_number, token)
    
    if not comments:
        return "✅ Нет комментариев в PR"
    
    # Классифицируем
    classified = {
        'useful': [],
        'warnings': [],
        'resolved': []
    }
    
    for comment in comments:
        if isinstance(comment, dict) and comment.get('body'):
            is_useful, comment_type, _ = analyze_comment(comment['body'])
            
            if is_useful and comment_type != "unprocessed":
                classified['useful'].append({
                    'user': comment.get('user', {}).get('login', 'Unknown'),
                    'body': comment['body'][:150],
                    'reason': comment_type
                })
            elif comment_type == "warning":
                classified['warnings'].append({
                    'user': comment.get('user', {}).get('login', 'Unknown'),
                    'body': comment['body'][:100],
                    'reason': comment_type
                })
            elif comment_type == "resolved":
                # Пропускаем уже разрешённые
                pass
    
    # Формируем отчёт
    summary = f"📊 Проверка PR #{pr_number}\n\n"
    
    if classified['useful']:
        summary += f"⚠️ Требуют исправлений: {len(classified['useful'])}\n\n"
        for i, comment in enumerate(classified['useful'][:3]):
            summary += f"{i}. @{comment['user']}: {comment['body']}\n"
        if len(classified['useful']) > 3:
            summary += f"   ... и ещё {len(classified['useful']) - 3}\n"
        
        summary += f"\n⚡ Действия:\n"
        summary += f"• Если критично → исправить и закрыть\n"
        summary += f"• Если не критично → можно отложить\n"
    elif classified['warnings']:
        summary += f"⚡ Предупреждения: {len(classified['warnings'])} (информационные, не требуют исправлений)\n\n"
        for i, comment in enumerate(classified['warnings'][:2]):
            summary += f"{i}. @{comment['user']}: {comment['body']}\n"
        if len(classified['warnings']) > 2:
            summary += f"   ... и ещё {len(classified['warnings']) - 2}\n"
        
        summary += f"ℹ️ Рекомендация: Предупреждения можно оставить без действий или закрыть после просмотра.\n"
    elif classified['resolved']:
        summary += f"ℹ️ Отмечено как resolved: {len(classified['resolved'])} (уже обработано)\n"
        for comment in classified['resolved'][:2]:
            summary += f"   @{comment['user']}\n"
    else:
        summary += "✅ Нет требуемых исправлений\n"
    
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
