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
    """Создает HTML страницу с оригинальным постом из Telegram (адаптировано под мобильные)"""
    
    if not data or not data.get('success'):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Ошибка загрузки | MTProto Proxy</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #0b141a;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
        }}
        .error-container {{
            width: 100%;
            max-width: 400px;
            background: #1f2c3c;
            border-radius: 18px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        }}
        .error-icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}
        .error-title {{
            color: #ff6b6b;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        .error-message {{
            color: #9aa8b9;
            font-size: 15px;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">❌</div>
        <div class="error-title">Ошибка загрузки</div>
        <div class="error-message">{data.get('error', 'Неизвестная ошибка')}</div>
        <div class="error-message">Канал: @ProxyMTProto</div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <meta name="theme-color" content="#17212b">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>MTProto Proxy | @ProxyMTProto</title>
    <style>
        /* Сброс стилей и базовые настройки */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #0b141a;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 12px;
            color: #fff;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Основной контейнер */
        .post-container {{
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
        }}
        
        /* Карточка поста */
        .post-card {{
            background: #17212b;
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            border: 1px solid #2b3945;
        }}
        
        /* Шапка с каналом */
        .post-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #2b3945;
        }}
        
        .channel-info {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .channel-avatar {{
            width: 40px;
            height: 40px;
            background: #2b5278;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}
        
        .channel-name {{
            font-weight: 600;
            font-size: 16px;
            color: #fff;
        }}
        
        .channel-handle {{
            font-size: 14px;
            color: #2ea6ff;
        }}
        
        .post-date {{
            font-size: 13px;
            color: #8e9eae;
            background: #232e3c;
            padding: 4px 10px;
            border-radius: 20px;
            white-space: nowrap;
        }}
        
        /* Контент поста (оригинальный Telegram) */
        .telegram-content {{
            background: #1e2a36;
            border-radius: 12px;
            padding: 16px;
            margin: 16px 0;
            border: 1px solid #2b3945;
        }}
        
        /* Стили для оригинальных элементов Telegram */
        .telegram-content .tgme_widget_message {{
            background: transparent !important;
            padding: 0 !important;
        }}
        
        .telegram-content .tgme_widget_message_text {{
            font-size: 15px !important;
            line-height: 1.5 !important;
            color: #e0e0e0 !important;
            margin-bottom: 16px !important;
        }}
        
        .telegram-content .tgme_widget_message_text a {{
            color: #2ea6ff !important;
            text-decoration: none !important;
        }}
        
        /* Стили для кнопки прокси (оригинальная) */
        .telegram-content .tgme_widget_message_button {{
            margin-top: 12px !important;
        }}
        
        .telegram-content .tgme_widget_message_button a {{
            display: inline-block !important;
            padding: 12px 20px !important;
            background: #2ea6ff !important;
            color: white !important;
            border-radius: 30px !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            text-decoration: none !important;
            width: 100% !important;
            text-align: center !important;
            transition: background 0.2s !important;
            -webkit-tap-highlight-color: transparent !important;
        }}
        
        .telegram-content .tgme_widget_message_button a:hover {{
            background: #1e8ad3 !important;
        }}
        
        .telegram-content .tgme_widget_message_button a:active {{
            transform: scale(0.98) !important;
        }}
        
        /* Статистика */
        .post-stats {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 16px 0 12px;
            padding: 12px 0;
            border-top: 1px solid #2b3945;
            border-bottom: 1px solid #2b3945;
        }}
        
        .views {{
            display: flex;
            align-items: center;
            gap: 6px;
            color: #8e9eae;
            font-size: 14px;
        }}
        
        .views-icon {{
            font-size: 16px;
        }}
        
        .original-link {{
            display: flex;
            align-items: center;
            gap: 4px;
            color: #2ea6ff;
            font-size: 14px;
            text-decoration: none;
            padding: 6px 12px;
            background: #232e3c;
            border-radius: 20px;
            transition: background 0.2s;
        }}
        
        .original-link:active {{
            background: #2b3945;
        }}
        
        /* Информация об обновлении */
        .footer-info {{
            margin-top: 16px;
            padding: 12px;
            background: #1e2a36;
            border-radius: 12px;
            text-align: center;
        }}
        
        .update-time {{
            font-size: 13px;
            color: #8e9eae;
            margin-bottom: 4px;
        }}
        
        .refresh-info {{
            font-size: 12px;
            color: #6a7a8a;
        }}
        
        /* Адаптация для очень маленьких экранов */
        @media (max-width: 380px) {{
            body {{
                padding: 8px;
            }}
            
            .post-card {{
                padding: 12px;
            }}
            
            .channel-avatar {{
                width: 36px;
                height: 36px;
                font-size: 18px;
            }}
            
            .channel-name {{
                font-size: 15px;
            }}
            
            .channel-handle {{
                font-size: 13px;
            }}
            
            .post-date {{
                font-size: 12px;
                padding: 3px 8px;
            }}
            
            .telegram-content .tgme_widget_message_text {{
                font-size: 14px !important;
            }}
            
            .telegram-content .tgme_widget_message_button a {{
                padding: 10px 16px !important;
                font-size: 14px !important;
            }}
        }}
        
        /* Для устройств с большим экраном центрируем */
        @media (min-width: 600px) {{
            body {{
                padding: 20px;
            }}
        }}
        
        /* Убираем выделение при тапе на мобильных */
        .no-tap-highlight {{
            -webkit-tap-highlight-color: transparent;
        }}
    </style>
</head>
<body>
    <div class="post-container">
        <div class="post-card">
            <!-- Шапка с информацией о канале -->
            <div class="post-header">
                <div class="channel-info">
                    <div class="channel-avatar">📢</div>
                    <div>
                        <div class="channel-name">Proxy MTProto</div>
                        <div class="channel-handle">@ProxyMTProto</div>
                    </div>
                </div>
                <div class="post-date">{data['date'][8:10]}.{data['date'][5:7]}.{data['date'][0:4]}</div>
            </div>
            
            <!-- Оригинальный пост из Telegram -->
            <div class="telegram-content">
                {data['post_html']}
            </div>
            
            <!-- Статистика и ссылки -->
            <div class="post-stats">
                <div class="views">
                    <span class="views-icon">👁</span>
                    <span>{data['views']}</span>
                </div>
                <a href="{data['url']}" target="_blank" class="original-link" rel="noopener noreferrer">
                    <span>🔗</span>
                    <span>Оригинал</span>
                </a>
            </div>
            
            <!-- Информация об обновлении -->
            <div class="footer-info">
                <div class="update-time">
                    Обновлено: {data['parsed_at'][8:10]}.{data['parsed_at'][5:7]}.{data['parsed_at'][0:4]} в {data['parsed_at'][11:16]}
                </div>
                <div class="refresh-info">
                    🔄 Автообновление раз в сутки
                </div>
            </div>
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
