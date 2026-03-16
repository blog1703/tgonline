import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def get_last_post(channel_name):
    """Получает последний пост из Telegram канала"""
    try:
        url = f"https://t.me/s/{channel_name}"
        print(f"Парсинг {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Ошибка HTTP: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим все сообщения
        messages = soup.find_all('div', class_='tgme_widget_message')
        
        if not messages:
            print("Сообщения не найдены")
            return None
        
        # Берем последнее (первое) сообщение
        latest = messages[0]
        
        # Извлекаем дату
        date_element = latest.find('time', class_='time')
        date = date_element['datetime'] if date_element else datetime.now().isoformat()
        
        # Извлекаем ссылку на пост
        link_element = latest.find('a', class_='tgme_widget_message_date')
        post_url = link_element['href'] if link_element else f"https://t.me/s/{channel_name}"
        
        # Извлекаем просмотры
        views_element = latest.find('span', class_='tgme_widget_message_views')
        views = views_element.text if views_element else '0'
        
        # Сохраняем ВЕСЬ HTML поста целиком
        post_html = str(latest)
        
        return {
            'success': True,
            'channel': channel_name,
            'post_html': post_html,
            'date': date,
            'url': post_url,
            'views': views,
            'parsed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return {'success': False, 'error': str(e)}

def generate_html(data):
    """Создает HTML страницу с оригинальным постом из Telegram"""
    
    if not data or not data.get('success'):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ошибка загрузки | MTProto Proxy</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #17212b; color: #fff; }}
        .error {{ background: #242f3d; border-radius: 12px; padding: 20px; text-align: center; color: #ff6b6b; }}
    </style>
</head>
<body>
    <div class="error">
        <h2>❌ Ошибка загрузки поста</h2>
        <p>{data.get('error', 'Неизвестная ошибка')}</p>
        <p>Канал: @ProxyMTProto</p>
    </div>
</body>
</html>"""
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Последний пост | @ProxyMTProto</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #17212b;
            color: #fff;
        }}
        .container {{
            background: #242f3d;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: #8e9eae;
            font-size: 14px;
        }}
        .channel-name {{
            color: #2ea6ff;
            font-weight: 600;
        }}
        .telegram-post {{
            background: #1e2a36;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #2ea6ff;
        }}
        .telegram-post a {{
            color: #2ea6ff;
            text-decoration: none;
        }}
        .telegram-post a:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #8e9eae;
            font-size: 13px;
            margin-top: 15px;
            text-align: center;
        }}
        .views {{
            display: inline-block;
            background: #1e2a36;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
        }}
        .refresh-info {{
            margin-top: 10px;
            font-size: 12px;
            color: #6a7a8a;
        }}
        /* Стили для кнопок Telegram */
        .tgme_widget_message_button {{
            margin-top: 10px;
        }}
        .tgme_widget_message_button a {{
            display: inline-block;
            padding: 8px 15px;
            background: #2ea6ff;
            color: white !important;
            border-radius: 20px;
            font-weight: 500;
            text-decoration: none !important;
        }}
        .tgme_widget_message_button a:hover {{
            background: #1e8ad3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="channel-name">📢 @ProxyMTProto</span>
            <span style="margin-left: auto;">📅 {data['date'][:10]}</span>
        </div>
        
        <div class="telegram-post">
            {data['post_html']}
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="views">👁 {data['views']} просмотров</span>
            <a href="{data['url']}" target="_blank" style="color: #2ea6ff; text-decoration: none;">🔗 Открыть в Telegram</a>
        </div>
        
        <div class="meta">
            <div>Обновлено: {data['parsed_at'][:19].replace('T', ' ')}</div>
            <div class="refresh-info">🔄 Обновляется раз в сутки</div>
        </div>
    </div>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    channel = os.environ.get('CHANNEL_NAME', 'ProxyMTProto')
    print(f"🚀 Начинаем парсинг канала @{channel}")
    
    # Получаем последний пост
    post_data = get_last_post(channel)
    
    if post_data and post_data.get('success'):
        print(f"✅ Пост получен от {post_data['date']}")
        print(f"📊 Просмотров: {post_data['views']}")
        print(f"📝 Размер HTML: {len(post_data['post_html'])} символов")
    else:
        print(f"❌ Ошибка: {post_data.get('error', 'Неизвестная ошибка')}")
    
    # Сохраняем JSON
    with open('latest_post.json', 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)
    
    # Генерируем HTML
    generate_html(post_data)
    
    print("✅ Готово! Файлы обновлены:")
    print("   - latest_post.json")
    print("   - index.html")

if __name__ == "__main__":
    main()
