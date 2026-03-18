import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import random
from datetime import datetime, timezone, timedelta  # Добавлен timedelta для сдвига часов

def get_last_posts(channel_name, limit=6):
    """Получает несколько последних постов из Telegram канала с обходом кэша"""
    try:
        # Добавляем случайный параметр для обхода кэша
        url = f"https://t.me/s/{channel_name}?r={random.randint(1, 1000000)}&before={int(time.time())}"
        print(f"Парсинг {url}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
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
            date = date_element['datetime'] if date_element else datetime.now(timezone.utc).isoformat()
            
            # Извлекаем ссылку на пост
            link_element = msg.find('a', class_='tgme_widget_message_date')
            post_url = link_element['href'] if link_element else f"https://t.me/s/{channel_name}"
            
            # Извлекаем просмотры
            views_element = msg.find('span', class_='tgme_widget_message_views')
            views = views_element.text if views_element else '0'
            
            # Извлекаем ТЕКСТ поста и форматируем его красиво
            text_element = msg.find('div', class_='tgme_widget_message_text')
            raw_text = text_element.get_text() if text_element else ''
            
            # Форматируем текст с переносами строк
            formatted_text = format_post_text(raw_text)
            
            # Сохраняем HTML поста для кнопок
            post_html = str(msg)
            
            posts.append({
                'id': i,
                'post_html': post_html,
                'post_text': formatted_text,
                'raw_text': raw_text,
                'date': date,
                'url': post_url,
                'views': views
            })
        
        return {
            'success': True,
            'channel': channel_name,
            'posts': posts,
            'parsed_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return {'success': False, 'error': str(e)}

def format_post_text(text):
    """Форматирует текст поста с правильными переносами строк"""
    if '\n' in text:
        return text
    
    text = re.sub(r'(Server:)', r'\n\1', text)
    text = re.sub(r'(Port:)', r'\n\1', text)
    text = re.sub(r'(Secret:)', r'\n\1', text)
    text = text.lstrip('\n')
    text = re.sub(r'(@ProxyMTProto)', r'\n\1', text)
    
    return text

def extract_connect_buttons(post_html):
    """Извлекает только кнопки Connect из HTML поста"""
    try:
        soup = BeautifulSoup(post_html, 'html.parser')
        buttons = soup.find_all('a', class_='tgme_widget_message_inline_button')
        
        if not buttons:
            return post_html
        
        buttons_html = ""
        for btn in buttons:
            buttons_html += str(btn)
        
        return buttons_html
    except:
        return post_html

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
    for i, post in enumerate(data['posts']):
        # Преобразуем дату из UTC в московское время (GMT+3)
        date_obj = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
        # Убеждаемся, что у объекта есть информация о часовом поясе (UTC)
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        # Прибавляем 3 часа для получения московского времени
        moscow_time = date_obj + timedelta(hours=3)
        # Форматируем для отображения
        formatted_date = moscow_time.strftime('%d.%m.%Y %H:%M')
        
        post_text = post['post_text']
        channel_link = f'<a href="https://t.me/ProxyMTProto" target="_blank" class="channel-link">@ProxyMTProto</a>'
        post_text = post_text.replace('@ProxyMTProto', channel_link)
        post_text_html = post_text.replace('\n', '<br>')
        
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
                
                <div class="post-text">
                    {post_text_html}
                </div>
                
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
        
        # Добавляем второй баннер после каждого 3-го поста (индекс 2, 5, 8...)
        if (i + 1) % 3 == 0:
            posts_html += f"""
            <!-- Баннер Astroproxy (на всю ширину) -->
            <div class="astro-banner" onclick="window.open('https://astroproxy.com/r/6b1442a44cbc36a3c277b86bb1f19e9b?lang=ru', '_blank')">
                <div class="astro-image-container">
                    <img src="https://raw.githubusercontent.com/blog1703/tgonline/refs/heads/main/images/astro.webp" 
                         alt="Astroproxy"
                         onerror="this.style.display='none'">
                </div>
                <div class="astro-text">
                    <div class="astro-slogan">Твой билет в мир PlayStation</div>
                    <div class="astro-description">С помощью прокси оплачивай подписки в Турции, США и других регионах без границ!</div>
                    <div class="astro-button-wrapper">
                        <a href="https://astroproxy.com/r/6b1442a44cbc36a3c277b86bb1f19e9b?lang=ru" 
                           class="astro-button" 
                           target="_blank" 
                           rel="noopener noreferrer">
                            Попробовать
                        </a>
                    </div>
                </div>
            </div>
            """
    
    # Преобразуем время последнего обновления в московское
    parsed_at = datetime.fromisoformat(data['parsed_at'].replace('Z', '+00:00'))
    if parsed_at.tzinfo is None:
        parsed_at = parsed_at.replace(tzinfo=timezone.utc)
    moscow_parsed = parsed_at + timedelta(hours=3)
    formatted_parsed = moscow_parsed.strftime('%d.%m.%Y %H:%M')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <meta name="theme-color" content="#17212b">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-capable" content="yes">
    
    <title>MTProto Proxy | Рабочие прокси для Telegram</title>
    
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <link rel="apple-touch-icon" href="favicon.ico">
    
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
            flex-direction: column;
            align-items: center;
            padding: 12px;
            color: #fff;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
        }}
        
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
        
        /* Полноразмерный баннер (Proxy Market) */
        .full-banner {{
            width: 100%;
            margin-bottom: 24px;
            border-radius: 16px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            background: linear-gradient(135deg, #1e3c5a 0%, #2b4f72 100%);
            border: 1px solid #3a6d99;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }}
        
        .full-banner:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 115, 230, 0.4);
        }}
        
        .full-banner:active {{
            transform: translateY(0);
        }}
        
        .banner-image-container {{
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px 20px 10px 20px;
        }}
        
        .full-banner img {{
            max-width: 100%;
            height: auto;
            max-height: 150px;
            object-fit: contain;
            border-radius: 12px;
        }}
        
        .banner-button-wrapper {{
            padding: 0 20px 20px 20px;
            display: flex;
            justify-content: center;
        }}
        
        .compact-button {{
            display: inline-block;
            background: rgb(0, 0, 255);
            color: white;
            padding: 10px 28px;
            border-radius: 40px;
            font-weight: 600;
            font-size: 15px;
            text-decoration: none;
            transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(0, 0, 255, 0.3);
            border: none;
            cursor: pointer;
            letter-spacing: 0.3px;
            width: auto;
            min-width: 200px;
            text-align: center;
        }}
        
        .compact-button:hover {{
            background: rgb(0, 0, 200);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 255, 0.4);
        }}
        
        .compact-button:active {{
            transform: translateY(0);
        }}
        
        /* Баннер Astroproxy (полная ширина, текст под картинкой) */
        .astro-banner {{
            width: 100%;
            margin: 16px 0;
            border-radius: 16px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            background: linear-gradient(135deg, #2a1e3a 0%, #4a2e5a 100%);
            border: 1px solid #6a4e7a;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }}
        
        .astro-banner:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(156, 39, 176, 0.4);
        }}
        
        .astro-banner:active {{
            transform: translateY(0);
        }}
        
        .astro-image-container {{
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px 20px 10px 20px;
        }}
        
        .astro-image-container img {{
            max-width: 100%;
            height: auto;
            max-height: 200px;
            object-fit: contain;
            border-radius: 12px;
        }}
        
        .astro-text {{
            padding: 0 20px 20px 20px;
            text-align: center;
        }}
        
        .astro-slogan {{
            font-size: 22px;
            font-weight: 700;
            color: #ffd700;
            margin-bottom: 10px;
            line-height: 1.3;
        }}
        
        .astro-description {{
            font-size: 15px;
            color: #e0e0e0;
            margin-bottom: 16px;
            line-height: 1.6;
            font-weight: 400;
            opacity: 0.95;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .astro-button-wrapper {{
            display: flex;
            justify-content: center;
        }}
        
        .astro-button {{
            display: inline-block;
            background: #ffd700;
            color: #2a1e3a;
            padding: 12px 32px;
            border-radius: 40px;
            font-weight: 700;
            font-size: 16px;
            text-decoration: none;
            transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
            border: none;
            cursor: pointer;
            letter-spacing: 0.5px;
        }}
        
        .astro-button:hover {{
            background: #ffed4a;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(255, 215, 0, 0.4);
        }}
        
        .astro-button:active {{
            transform: translateY(0);
        }}
        
        .posts-feed {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 20px;
        }}
        
        .post-card {{
            background: #17212b;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            border: 1px solid #2b3945;
        }}
        
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
        
        .post-text {{
            background: #1e2a36;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 14px;
            line-height: 1.8;
            color: #e0e0e0;
            white-space: pre-line;
            word-break: break-word;
            border-left: 3px solid #2ea6ff;
        }}
        
        .channel-link {{
            color: #2ea6ff;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .channel-link:hover {{
            text-decoration: underline;
        }}
        
        .telegram-buttons {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
            margin: 16px 0 8px;
        }}
        
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
            transform: translateY(-1px);
        }}
        
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
        
        .original-link:hover {{
            background: #2b3945;
        }}
        
        .footer {{
            margin-top: 16px;
            padding: 12px;
            background: #1e2a36;
            border-radius: 8px;
            text-align: center;
            font-size: 11px;
            color: #8e9eae;
        }}
        
        @media (max-width: 480px) {{
            .post-card {{
                padding: 12px;
            }}
            
            .post-text {{
                font-size: 13px;
                padding: 12px;
            }}
            
            .telegram-buttons {{
                gap: 8px;
            }}
            
            .telegram-buttons .tgme_widget_message_inline_button {{
                padding: 6px 16px !important;
                font-size: 13px !important;
                min-width: 80px !important;
            }}
            
            .full-banner img {{
                max-height: 120px;
            }}
            
            .compact-button {{
                min-width: 160px;
                padding: 8px 20px;
                font-size: 14px;
            }}
            
            .astro-image-container img {{
                max-height: 150px;
            }}
            
            .astro-slogan {{
                font-size: 18px;
            }}
            
            .astro-description {{
                font-size: 13px;
            }}
            
            .astro-button {{
                padding: 10px 28px;
                font-size: 15px;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="site-header">
            <div class="site-title">MTProto Proxy</div>
            <div class="site-description">@ProxyMTProto • рабочие прокси для Telegram</div>
        </div>
        
        <div class="info-compact">
            <span class="info-compact-text">🔒 Нажми Connect → Открой в Telegram → Проверь статус прокси → Подключить прокси</span>
        </div>
        
        <!-- Полноразмерный баннер с компактной кнопкой -->
        <div class="full-banner" onclick="window.open('https://ru.dashboard.proxy.market/?ref=E000143973', '_blank')">
            <div class="banner-image-container">
                <img src="https://raw.githubusercontent.com/blog1703/tgonline/refs/heads/main/images/banner_pm.webp" 
                     alt="Proxy Market"
                     onerror="this.style.display='none'">
            </div>
            <div class="banner-button-wrapper">
                <a href="https://ru.dashboard.proxy.market/?ref=E000143973" 
                   class="compact-button" 
                   target="_blank" 
                   rel="noopener noreferrer">
                    Надёжные прокси за 49 ₽
                </a>
            </div>
        </div>
        
        <div class="posts-feed">
            {posts_html}
        </div>
        
        <div class="footer">
            <div>Обновлено: {formatted_parsed} (МСК)</div>
            <div style="margin-top: 4px;">🔄 Автообновление каждые 30 минут</div>
        </div>
    </div>
    
    <script type="text/javascript">
    var sc_project=13211351; 
    var sc_invisible=0; 
    var sc_security="28a55aa9"; 
    var scJsHost = "https://";
    document.write("<sc"+"ript type='text/javascript' src='" + scJsHost+
    "statcounter.com/counter/counter.js'></"+"script>");
    </script>
    <noscript><div class="statcounter"><a title="Web Analytics Made Easy -
    Statcounter" href="https://statcounter.com/" target="_blank"><img
    class="statcounter" src="https://c.statcounter.com/13211351/0/28a55aa9/1/"
    alt="Web Analytics Made Easy - Statcounter"
    referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
    
</body>
</html>"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    channel = os.environ.get('CHANNEL_NAME', 'ProxyMTProto')
    print(f"🚀 Начинаем парсинг канала @{channel}")
    
    post_data = get_last_posts(channel, limit=6)
    
    if post_data and post_data.get('success'):
        print(f"✅ Получено {len(post_data['posts'])} постов")
        for i, post in enumerate(post_data['posts']):
            print(f"   Пост {i+1}: {post['date']}, просмотров: {post['views']}")
            print(f"      Текст: {post['post_text'][:50]}...")
    else:
        print(f"❌ Ошибка: {post_data.get('error', 'Неизвестная ошибка')}")
    
    with open('latest_post.json', 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)
    
    generate_html(post_data)
    
    print("✅ Готово! Файлы обновлены:")
    print("   - latest_post.json")
    print("   - index.html")

if __name__ == "__main__":
    main()
