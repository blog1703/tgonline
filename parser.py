import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

def get_last_post(channel_name):
    """Получает последний пост из Telegram канала"""
    try:
        url = f"https://t.me/s/{channel_name}"
        print(f"Парсинг {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        
        # Извлекаем текст
        text_element = latest.find('div', class_='tgme_widget_message_text')
        text = text_element.get_text() if text_element else ''
        
        # Извлекаем дату
        date_element = latest.find('time', class_='time')
        date = date_element['datetime'] if date_element else datetime.now().isoformat()
        
        # Извлекаем ссылку на пост
        link_element = latest.find('a', class_='tgme_widget_message_date')
        post_url = link_element['href'] if link_element else f"https://t.me/s/{channel_name}"
        
        # Извлекаем просмотры
        views_element = latest.find('span', class_='tgme_widget_message_views')
        views = views_element.text if views_element else '0'
        
        # Парсим данные прокси из текста
        proxy_data = parse_proxy_data(text)
        
        return {
            'success': True,
            'channel': channel_name,
            'text': text,
            'date': date,
            'url': post_url,
            'views': views,
            'proxy': proxy_data,
            'parsed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return {'success': False, 'error': str(e)}

def parse_proxy_data(text):
    """Извлекает данные прокси из текста поста"""
    proxy = {
        'server': '',
        'port': '',
        'secret': ''
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if 'Server:' in line:
            proxy['server'] = line.replace('Server:', '').strip()
        elif 'Port:' in line:
            proxy['port'] = line.replace('Port:', '').strip()
        elif 'Secret:' in line:
            secret = line.replace('Secret:', '').strip()
            # Убираем @username если есть
            if '@' in secret:
                secret = secret.split('@')[0].strip()
            proxy['secret'] = secret
    
    return proxy

def generate_html(data):
    """Создает HTML страницу с постом"""
    
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
    
    p = data['proxy']
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Последний прокси | @ProxyMTProto</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #17212b;
            color: #fff;
        }}
        .post {{
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
        .original-text {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            white-space: pre-wrap;
            background: #1e2a36;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #2ea6ff;
            line-height: 1.5;
        }}
        .proxy-card {{
            background: #1e2a36;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            border: 1px solid #3e546c;
        }}
        .proxy-row {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid #2e4053;
        }}
        .proxy-row:last-child {{
            border-bottom: none;
        }}
        .proxy-label {{
            width: 80px;
            color: #8e9eae;
        }}
        .proxy-value {{
            flex: 1;
            color: #2ea6ff;
            font-family: monospace;
            word-break: break-all;
        }}
        .connect-btn {{
            background: #2ea6ff;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: background 0.2s;
            margin: 10px 0;
        }}
        .connect-btn:hover {{
            background: #1e8ad3;
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
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
        }}
        .refresh-info {{
            margin-top: 10px;
            font-size: 12px;
            color: #6a7a8a;
        }}
    </style>
</head>
<body>
    <div class="post">
        <div class="header">
            <span class="channel-name">📢 @ProxyMTProto</span>
            <span style="margin-left: auto;">{data['date'][:10]}</span>
        </div>
        
        <div class="original-text">
            {data['text'].replace(chr(10), '<br>')}
        </div>
        
        <div class="proxy-card">
            <div class="proxy-row">
                <span class="proxy-label">🌍 Server:</span>
                <span class="proxy-value" id="server">{p['server'] or '—'}</span>
            </div>
            <div class="proxy-row">
                <span class="proxy-label">🔌 Port:</span>
                <span class="proxy-value" id="port">{p['port'] or '—'}</span>
            </div>
            <div class="proxy-row">
                <span class="proxy-label">🔑 Secret:</span>
                <span class="proxy-value" id="secret">{p['secret'][:30] + '...' if p['secret'] else '—'}</span>
            </div>
        </div>
        
        <button class="connect-btn" onclick="connectToProxy()">
            📲 Подключиться в Telegram
        </button>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="views">👁 {data['views']} просмотров</span>
            <a href="{data['url']}" target="_blank" style="color: #2ea6ff; text-decoration: none;">🔗 Оригинал</a>
        </div>
        
        <div class="meta">
            <div>Обновлено: {data['parsed_at'][:19].replace('T', ' ')}</div>
            <div class="refresh-info">🔄 Автообновление каждые 15 минут</div>
        </div>
    </div>
    
    <script>
    function connectToProxy() {{
        const server = document.getElementById('server').textContent;
        const port = document.getElementById('port').textContent;
        const secret = document.getElementById('secret').textContent.replace('...', '');
        
        if (server && port && server !== '—' && port !== '—') {{
            const tgLink = `tg://proxy?server=${{encodeURIComponent(server)}}&port=${{encodeURIComponent(port)}}&secret=${{encodeURIComponent(secret)}}`;
            
            // Пробуем открыть Telegram
            window.location.href = tgLink;
            
            // Если не открылось, показываем данные для ручного ввода
            setTimeout(() => {{
                if (!document.hidden) {{
                    const proxyText = `Сервер: ${{server}}\nПорт: ${{port}}\nSecret: ${{secret}}`;
                    if (confirm('Telegram не открылся?\\n\\nСкопировать данные прокси?')) {{
                        navigator.clipboard.writeText(proxyText).then(() => {{
                            alert('✅ Данные скопированы!\\n\\nВставьте их вручную в Telegram:\\n\\n' + proxyText);
                        }});
                    }}
                }}
            }}, 500);
        }} else {{
            alert('❌ В этом посте нет данных прокси');
        }}
    }}
    </script>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    channel = os.environ.get('CHANNEL_NAME', 'ProxyMTProto')
    print(f"🚀 Начинаем парсинг канала @{channel}")
    
    # Получаем последний пост
    post_data = get_last_post(channel)
    
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
