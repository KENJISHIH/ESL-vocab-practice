// Service worker：讓網站加到主畫面後，沒網路也能開
// 策略分兩種：
//   程式與單字資料 → network-first（有網路時永遠拿到最新版，沒網路才用快取）
//   音檔與圖片     → cache-first（檔案大又幾乎不變，抓過一次就不再重抓）
const CACHE = 'esl-vocab-v1';

// 檔名符合這些副檔名的走 cache-first
const CACHE_FIRST = /\.(m4a|png|ico|jpg|jpeg|svg)$/i;

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

// 抓到就順手存一份
function cachePut(req, res) {
    if (res && res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
    }
    return res;
}

self.addEventListener('fetch', e => {
    const req = e.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);
    if (url.origin !== self.location.origin) return;   // 只管自己站上的資源

    if (CACHE_FIRST.test(url.pathname)) {
        e.respondWith(
            caches.match(req).then(hit => hit || fetch(req).then(res => cachePut(req, res)))
        );
        return;
    }

    e.respondWith(
        fetch(req)
            .then(res => cachePut(req, res))
            .catch(() => caches.match(req))
    );
});
