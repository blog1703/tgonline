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
            
            # Сохраняем HTML поста
            post_html = str(msg)
            
            posts.append({
                'id': i,
                'post_html': post_html,
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
                
                <div class="telegram-content">
                    {post['post_html']}
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
        
        /* Карточка поста - ПРЕЖНИЙ СТИЛЬ */
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
        
        /* Контент поста - ПРЕЖНИЙ СТИЛЬ */
        .telegram-content {{
            background: #1e2a36;
            border-radius: 8px;
            padding: 12px;
            margin: 12px 0;
            font-size: 13px;
            line-height: 1.5;
            color: #e0e0e0;
        }}
        
        /* Стили для текста поста */
        .telegram-content .tgme_widget_message_text {{
            font-size: 13px !important;
            line-height: 1.5 !important;
            color: #e0e0e0 !important;
            margin-bottom: 12px !important;
        }}
        
        /* ===== ЭЛЕГАНТНЫЕ КНОПКИ CONNECT ===== */
        /* Вертикальное расположение */
        .telegram-content .tgme_widget_message_inline_row {{
            display: flex !important;
            flex-direction: column !important;
            gap: 8px !important;
            width: 100% !important;
            margin: 8px 0 !important;
        }}
        
        /* Стиль кнопок - МЕНЬШЕ И ЭЛЕГАНТНЕЕ */
        .telegram-content .tgme_widget_message_inline_row .tgme_widget_message_inline_button {{
            display: inline-block !important;
            width: auto !important;
            min-width: 120px !important;
            max-width: 200px !important;
            margin: 0 auto !important;
            padding: 8px 20px !important;
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
            letter-spacing: 0.3px !important;
        }}
        
        /* Эффект при наведении */
        .telegram-content .tgme_widget_message_inline_row .tgme_widget_message_inline_button:hover {{
            background: #1e8ad3 !important;
            box-shadow: 0 4px 10px rgba(46, 166, 255, 0.3) !important;
        }}
        
        /* Стиль для текста кнопки */
        .telegram-content .tgme_widget_message_inline_button .tgme_widget_message_inline_button_text {{
            color: white !important;
            font-weight: 500 !important;
        }}
        
        /* Скрываем лишние символы */
        .telegram-content .tgme_widget_message_user,
        .telegram-content .tgme_widget_message_bubble,
        .telegram-content .tgme_widget_message > div:empty {{
            display: none !important;
        }}
        /* ===== КОНЕЦ СТИЛЕЙ КНОПОК ===== */
        
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
            .post-card {{
                padding: 12px;
            }}
            
            .telegram-content .tgme_widget_message_inline_row .tgme_widget_message_inline_button {{
                min-width: 100px !important;
                padding: 6px 16px !important;
                font-size: 13px !important;
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

def main():
    channel = os.environ.get('CHANNEL_NAME', 'ProxyMTProto')
    print(f"🚀 Начинаем парсинг канала @{channel}")
    
    # Получаем последние 4 поста
    post_data = get_last_posts(channel, limit=4)
    
    if post_data and post_data.get('success'):
        print(f"✅ Получено {len(post_data['posts'])} постов")
        for i, post in enumerate(post_data['posts']):
            print(f"   Пост {i+1}: {post['date']}, просмотров: {post['views']}")
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
