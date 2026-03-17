import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def get_last_posts(channel_name, limit=4):
    """Получает несколько последних постов из Telegram канала"""
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
        
        # Берем нужное количество последних постов
        posts = []
        for i, msg in enumerate(messages[:limit]):
            # Извлекаем дату
            date_element = msg.find('time', class_='time')
            date = date_element['datetime'] if date_element else datetime.now().isoformat()
            
            # Извлекаем ссылку на пост
            link_element = msg.find('a', class_='tgme_widget_message_date')
            post_url = link_element['href'] if link_element else f"https://t.me/s/{channel_name}"
            
            # Извлекаем просмотры
            views_element = msg.find('span', class_='tgme_widget_message_views')
            views = views_element.text if views_element else '0'
            
            # Извлекаем ТЕКСТ поста (информацию о сервере, порте, секрете)
            text_element = msg.find('div', class_='tgme_widget_message_text')
            post_text = text_element.get_text() if text_element else ''
            
            # Сохраняем HTML поста
            post_html = str(msg)
            
            posts.append({
                'id': i,
                'post_html': post_html,
                'post_text': post_text,
                'date': date,
                'url': post_url,
                'views': views
            })
        
        return {
            'success': True,
            'channel': channel_name,
            'posts': posts,
            'parsed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return {'success': False, 'error': str(e)}

def generate_html(data):
    """Создает HTML страницу с лентой постов"""
    
    if not data or not data.get('success'):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>MTProto Proxy | Telegram прокси</title>
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
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
    
    posts_html = ""
    for post in data['posts']:
        # Форматируем дату для отображения
        date_obj = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
        
        # Форматируем текст поста для отображения (заменяем переносы строк на <br>)
        formatted_text = post['post_text'].replace('\n', '<br>')
        
        posts_html += f"""
            <div class="post-card">
                <div class="post-header">
                    <div class="channel-info">
                        <div class="channel-avatar">📢</div>
                        <div>
                            <div class="channel-name">Proxy MTProto</div>
                            <div class="channel-handle">@ProxyMTProto</div>
                        </div>
                    </div>
                    <div class="post-date">{formatted_date}</div>
                </div>
                
                <!-- ТЕКСТ ПОСТА (сервер, порт, секрет) -->
                <div class="post-text">
                    {formatted_text}
                </div>
                
                <!-- КНОПКИ CONNECT (оригинальные из Telegram) -->
                <div class="telegram-buttons">
                    {extract_connect_buttons(post['post_html'])}
                </div>
                
                <div class="post-stats">
                    <div class="views">
                        <span class="views-icon">👁</span>
                        <span>{post['views']}</span>
                    </div>
                    <a href="{post['url']}" target="_blank" class="original-link" rel="noopener noreferrer">
                        <span>🔗</span>
                        <span>Оригинал</span>
                    </a>
                </div>
            </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <meta name="theme-color" content="#17212b">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>MTProto Proxy | Рабочие прокси для Telegram</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <link rel="apple-touch-icon" href="favicon.ico">
    
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
            padding: 12px;
            color: #fff;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Основной контейнер */
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        /* Шапка сайта */
        .site-header {{
            margin-bottom: 16px;
            text-align: center;
        }}
        
        .site-title {{
            font-size: 24px;
            font-weight: 700;
            color: #2ea6ff;
            margin-bottom: 4px;
        }}
        
        .site-description {{
            font-size: 13px;
            color: #8e9eae;
        }}
        
        /* Компактный информационный блок */
        .info-compact {{
            background: linear-gradient(135deg, #1e3c5a 0%, #2b4f72 100%);
            border-radius: 50px;
            padding: 10px 16px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #3a6d99;
            font-size: 13px;
            color: #fff;
        }}
        
        .info-compact-text {{
            color: #fff;
        }}
        
        /* Баннер для реферальной ссылки (ЗАГЛУШКА) */
        .banner {{
            background: linear-gradient(135deg, #1e3c5a 0%, #2b4f72 100%);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #3a6d99;
            box-shadow: 0 4px 12px rgba(46, 166, 255, 0.2);
            cursor: pointer;
            transition: transform 0.2s;
        }}
        
        .banner:hover {{
            transform: translateY(-2px);
        }}
        
        .banner:active {{
            transform: translateY(0);
        }}
        
        .banner-title {{
            font-size: 16px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 4px;
        }}
        
        .banner-text {{
            font-size: 13px;
            color: #c9e1f2;
            margin-bottom: 8px;
        }}
        
        .banner-button {{
            display: inline-block;
            background: #ffd700;
            color: #1e3c5a;
            padding: 8px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            transition: background 0.2s;
        }}
        
        /* Лента постов */
        .posts-feed {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 20px;
        }}
        
        /* Карточка поста */
        .post-card {{
            background: #17212b;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            border: 1px solid #2b3945;
        }}
        
        /* Шапка поста */
        .post-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #2b3945;
        }}
        
        .channel-info {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .channel-avatar {{
            width: 36px;
            height: 36px;
            background: #2b5278;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }}
        
        .channel-name {{
            font-weight: 500;
            font-size: 15px;
            color: #fff;
        }}
        
        .channel-handle {{
            font-size: 12px;
            color: #8e9eae;
        }}
        
        .post-date {{
            font-size: 11px;
            color: #8e9eae;
            background: #1e2a36;
            padding: 4px 8px;
            border-radius: 12px;
        }}
        
        /* Текст поста (сервер, порт, секрет) */
        .post-text {{
            background: #1e2a36;
            border-radius: 8px;
            padding: 12px;
            margin: 12px 0;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: #e0e0e0;
            white-space: pre-wrap;
            word-break: break-word;
            border-left: 3px solid #2ea6ff;
        }}
        
        /* Контейнер для кнопок Connect */
        .telegram-buttons {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin: 16px 0 8px;
        }}
        
        /* Стили для кнопок Connect - в ряд */
        .telegram-buttons .tgme_widget_message_inline_button {{
            display: inline-block !important;
            padding: 8px 24px !important;
            background: #2ea6ff !important;
            color: white !important;
            border-radius: 30px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            text-decoration: none !important;
            text-align: center !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(46, 166, 255, 0.2) !important;
            transition: all 0.2s ease !important;
            min-width: 100px !important;
        }}
        
        .telegram-buttons .tgme_widget_message_inline_button:hover {{
            background: #1e8ad3 !important;
            box-shadow: 0 4px 10px rgba(46, 166, 255, 0.3) !important;
        }}
        
        /* Скрываем лишние элементы из оригинального HTML */
        .telegram-buttons .tgme_widget_message_user,
        .telegram-buttons .tgme_widget_message_bubble,
        .telegram-buttons .tgme_widget_message > div:empty {{
            display: none !important;
        }}
        
        /* Статистика поста */
        .post-stats {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid #2b3945;
        }}
        
        .views {{
            display: flex;
            align-items: center;
            gap: 4px;
            color: #8e9eae;
            font-size: 12px;
        }}
        
        .original-link {{
            display: flex;
            align-items: center;
            gap: 4px;
            color: #2ea6ff;
            font-size: 12px;
            text-decoration: none;
            padding: 4px 10px;
            background: #1e2a36;
            border-radius: 16px;
        }}
        
        /* Подвал */
        .footer {{
            margin-top: 16px;
            padding: 12px;
            background: #1e2a36;
            border-radius: 8px;
            text-align: center;
            font-size: 11px;
            color: #8e9eae;
        }}
        
        /* Адаптация для мобильных */
        @media (max-width: 480px) {{
            .telegram-buttons {{
                gap: 8px;
            }}
            
            .telegram-buttons .tgme_widget_message_inline_button {{
                padding: 6px 16px !important;
                font-size: 13px !important;
                min-width: 80px !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Шапка сайта -->
        <div class="site-header">
            <div class="site-title">MTProto Proxy</div>
            <div class="site-description">@ProxyMTProto • рабочие прокси для Telegram</div>
        </div>
        
        <!-- Компактный информационный блок -->
        <div class="info-compact">
            <span class="info-compact-text">🔒 Нажми Connect → Открой в Telegram → Подключи</span>
        </div>
        
        <!-- Баннер для реферальной ссылки -->
        <div class="banner" onclick="window.open('https://telegram.org', '_blank')">
            <div class="banner-title">✨ Место для вашей рекламы ✨</div>
            <div class="banner-text">Здесь может быть ваша реферальная ссылка</div>
            <div class="banner-button">Перейти</div>
        </div>
        
        <!-- Лента последних постов -->
        <div class="posts-feed">
            {posts_html}
        </div>
        
        <!-- Подвал -->
        <div class="footer">
            <div>Обновлено: {datetime.fromisoformat(data['parsed_at'].replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')}</div>
            <div style="margin-top: 4px;">🔄 Автообновление раз в сутки</div>
        </div>
    </div>
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def extract_connect_buttons(post_html):
    """Извлекает только кнопки Connect из HTML поста"""
    try:
        soup = BeautifulSoup(post_html, 'html.parser')
        # Находим все inline кнопки
        buttons = soup.find_all('a', class_='tgme_widget_message_inline_button')
        
        if not buttons:
            return post_html
        
        # Создаем HTML только для кнопок
        buttons_html = ""
        for btn in buttons:
            buttons_html += str(btn)
        
        return buttons_html
    except:
        return post_html

def main():
    channel = os.environ.get('CHANNEL_NAME', 'ProxyMTProto')
    print(f"🚀 Начинаем парсинг канала @{channel}")
    
    # Получаем последние 4 поста
    post_data = get_last_posts(channel, limit=4)
    
    if post_data and post_data.get('success'):
        print(f"✅ Получено {len(post_data['posts'])} постов")
        for i, post in enumerate(post_data['posts']):
            print(f"   Пост {i+1}: {post['date']}, просмотров: {post['views']}")
            print(f"      Текст: {post['post_text'][:50]}...")
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
