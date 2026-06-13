/* 简单的 PWA Service Worker:
 * - 预缓存应用外壳, 让已安装的 App 二次打开更快、弱网下也能进入界面
 * - 静态资源走 cache-first, /api 行情请求始终走网络(不缓存预测结果)
 */
const CACHE = 'stock-step-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
    ).then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  // 行情/分析接口: 永远走网络, 拿不到再返回离线提示
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(
        () => new Response(JSON.stringify({ detail: '离线状态, 无法获取行情数据' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    );
    return;
  }

  // 静态资源: 命中缓存优先, 否则取网络并回填缓存
  event.respondWith(
    caches.match(request).then(
      (cached) =>
        cached ||
        fetch(request).then((resp) => {
          if (resp.ok && url.origin === self.location.origin) {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(request, copy));
          }
          return resp;
        }).catch(() => caches.match('./index.html')),
    ),
  );
});
