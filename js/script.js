(function(){
    const PROXY_LIST_URL = 'https://blog1703.github.io/tgonline/proxies.txt';
    const FETCH_TIMEOUT = 10000;
    const AUTO_REFRESH_INTERVAL = 30 * 60 * 1000;

    let cachedProxies = [];
    let currentIndex = -1;
    let currentProxyUrl = '';
    let isLoading = false;
    let lastContentHash = '';

    const getProxyBtn = document.getElementById('getProxyBtn');
    const resultArea = document.getElementById('resultArea');
    const proxyLinkDiv = document.getElementById('proxyLink');
    const connectBtn = document.getElementById('connectBtn');
    const statusMsg = document.getElementById('statusMsg');
    const updateTimeSpan = document.getElementById('updateTime');
    const totalCountSpan = document.getElementById('totalCount');
    const attemptNumSpan = document.getElementById('attemptNum');
    const totalNumSpan = document.getElementById('totalNum');

    function simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0;
        }
        return hash.toString();
    }

    async function fetchWithTimeout(url, timeout = FETCH_TIMEOUT) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        try {
            const response = await fetch(url, { signal: controller.signal });
            clearTimeout(timeoutId);
            return response;
        } catch (err) {
            clearTimeout(timeoutId);
            throw err;
        }
    }

    async function loadProxies(force = false) {
        if (isLoading) return false;
        isLoading = true;
        statusMsg.innerHTML = '<span class="loader"></span> Загрузка...';
        getProxyBtn.disabled = true;
        try {
            const response = await fetchWithTimeout(PROXY_LIST_URL);
            if (!response.ok) throw new Error('HTTP ' + response.status);
            const text = await response.text();
            const newHash = simpleHash(text);
            if (!force && lastContentHash === newHash && cachedProxies.length > 0) {
                statusMsg.textContent = 'Список актуален';
                getProxyBtn.disabled = false;
                isLoading = false;
                return true;
            }
            lastContentHash = newHash;
            const updateMatch = text.match(/# Updated: (.*?)(?:\n|$)/);
            if (updateMatch) updateTimeSpan.textContent = 'Обновлено: ' + updateMatch[1];
            const proxies = text.split('\n').filter(line => line.trim().startsWith('tg://'));
            if (!proxies.length) throw new Error('Список пуст');
            cachedProxies = proxies;
            if (cachedProxies.length === 0) currentIndex = -1;
            totalCountSpan.textContent = proxies.length;
            totalNumSpan.textContent = proxies.length;
            statusMsg.textContent = 'Готово';
            getProxyBtn.disabled = false;
            isLoading = false;
            return true;
        } catch (err) {
            statusMsg.textContent = err.name === 'AbortError' ? 'Ошибка: таймаут загрузки' : 'Ошибка загрузки';
            getProxyBtn.disabled = false;
            isLoading = false;
            return false;
        }
    }

    function showNextProxy() {
        if (!cachedProxies.length) return false;
        currentIndex = (currentIndex + 1) % cachedProxies.length;
        currentProxyUrl = cachedProxies[currentIndex];
        proxyLinkDiv.textContent = currentProxyUrl;
        attemptNumSpan.textContent = currentIndex + 1;
        return true;
    }

    async function handleGetProxy() {
        if (isLoading) { statusMsg.textContent = 'Загрузка, подождите...'; return; }
        if (!cachedProxies.length) { const loaded = await loadProxies(); if (!loaded) return; }
        getProxyBtn.disabled = true;
        getProxyBtn.innerHTML = '<span class="loader"></span> Поиск';
        const success = showNextProxy();
        if (success) {
            resultArea.style.display = 'block';
            statusMsg.textContent = 'Готово';
        } else {
            statusMsg.textContent = 'Нет доступных прокси';
        }
        getProxyBtn.disabled = false;
        getProxyBtn.textContent = 'Получить рабочий прокси';
    }

    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            return success;
        }
    }

    proxyLinkDiv.addEventListener('click', async () => {
        if (currentProxyUrl) {
            const ok = await copyToClipboard(currentProxyUrl);
            if (ok) {
                statusMsg.textContent = '✅ Ссылка скопирована!';
                setTimeout(() => { if (statusMsg.textContent === '✅ Ссылка скопирована!') statusMsg.textContent = 'Готово'; }, 2000);
            } else {
                statusMsg.textContent = '❌ Ошибка копирования';
            }
        }
    });

    connectBtn.addEventListener('click', () => {
        if (currentProxyUrl) window.open(currentProxyUrl, '_blank');
    });

    async function autoRefresh() {
        if (isLoading) return;
        try {
            const response = await fetchWithTimeout(PROXY_LIST_URL);
            if (!response.ok) return;
            const text = await response.text();
            const newHash = simpleHash(text);
            if (newHash !== lastContentHash && cachedProxies.length > 0) {
                await loadProxies(true);
                statusMsg.textContent = 'Список обновлён';
                setTimeout(() => { if (statusMsg.textContent === 'Список обновлён') statusMsg.textContent = 'Готово'; }, 2000);
            }
        } catch(e) {}
    }

    getProxyBtn.addEventListener('click', handleGetProxy);
    setInterval(autoRefresh, AUTO_REFRESH_INTERVAL);
    loadProxies();

    document.querySelectorAll('.faq-question').forEach(item => {
        item.addEventListener('click', () => {
            const parent = item.parentElement;
            parent.classList.toggle('active');
        });
    });

    const burgerIcon = document.getElementById('burgerIcon');
    const mobileMenu = document.getElementById('mobileMenu');
    const closeMenu = document.getElementById('closeMenu');
    if (burgerIcon && mobileMenu) {
        const toggleMenu = () => mobileMenu.classList.toggle('show');
        burgerIcon.addEventListener('click', toggleMenu);
        if (closeMenu) closeMenu.addEventListener('click', toggleMenu);
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) toggleMenu();
        });
    }
})();
