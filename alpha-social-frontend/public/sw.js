// Alpha Social PWA Service Worker
const CACHE_NAME = 'alpha-social-v1.0.0';
const API_CACHE_NAME = 'alpha-social-api-v1.0.0';

// 需要缓存的静态资源
const STATIC_CACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192x192.png',
  '/icon-512x512.png'
];

// API缓存策略
const API_CACHE_PATTERNS = [
  /^https?:\/\/localhost:5000\/api\//,
  /^https?:\/\/.*\.alpha-social\.com\/api\//
];

// 安装事件 - 缓存静态资源
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static resources');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('[SW] Installation complete');
        return self.skipWaiting();
      })
  );
});

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Activation complete');
        return self.clients.claim();
      })
  );
});

// 拦截网络请求
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 处理API请求
  if (isApiRequest(request.url)) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // 处理静态资源请求
  if (request.method === 'GET') {
    event.respondWith(handleStaticRequest(request));
    return;
  }
});

// 检查是否为API请求
function isApiRequest(url) {
  return API_CACHE_PATTERNS.some(pattern => pattern.test(url));
}

// 处理API请求 - 网络优先，缓存备用
async function handleApiRequest(request) {
  const cache = await caches.open(API_CACHE_NAME);
  
  try {
    // 尝试网络请求
    const networkResponse = await fetch(request);
    
    // 如果请求成功，缓存响应
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache for:', request.url);
    
    // 网络失败，尝试从缓存获取
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 如果缓存也没有，返回离线页面或错误响应
    return new Response(
      JSON.stringify({
        error: '网络连接失败，请检查网络设置',
        offline: true
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// 处理静态资源请求 - 缓存优先，网络备用
async function handleStaticRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  
  // 先尝试从缓存获取
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    // 缓存没有，尝试网络请求
    const networkResponse = await fetch(request);
    
    // 缓存新的响应
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Failed to fetch:', request.url);
    
    // 如果是导航请求，返回主页
    if (request.mode === 'navigate') {
      const indexResponse = await cache.match('/index.html');
      if (indexResponse) {
        return indexResponse;
      }
    }
    
    // 返回网络错误
    return new Response('网络连接失败', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// 后台同步事件
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'background-sync-posts') {
    event.waitUntil(syncPendingPosts());
  }
});

// 同步待发布的帖子
async function syncPendingPosts() {
  try {
    // 从IndexedDB获取待同步的帖子
    const pendingPosts = await getPendingPosts();
    
    for (const post of pendingPosts) {
      try {
        const response = await fetch('/api/contents', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(post)
        });
        
        if (response.ok) {
          // 同步成功，从待同步列表中移除
          await removePendingPost(post.id);
          console.log('[SW] Post synced successfully:', post.id);
        }
      } catch (error) {
        console.log('[SW] Failed to sync post:', post.id, error);
      }
    }
  } catch (error) {
    console.log('[SW] Background sync failed:', error);
  }
}

// 推送通知事件
self.addEventListener('push', (event) => {
  console.log('[SW] Push received');
  
  const options = {
    body: '您有新的消息',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '查看详情',
        icon: '/icon-192x192.png'
      },
      {
        action: 'close',
        title: '关闭',
        icon: '/icon-192x192.png'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.data = { ...options.data, ...data };
  }
  
  event.waitUntil(
    self.registration.showNotification('Alpha Social', options)
  );
});

// 通知点击事件
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    // 打开应用
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// 辅助函数 - 获取待同步的帖子（模拟）
async function getPendingPosts() {
  // 实际实现中应该从IndexedDB获取
  return [];
}

// 辅助函数 - 移除已同步的帖子（模拟）
async function removePendingPost(postId) {
  // 实际实现中应该从IndexedDB移除
  console.log('[SW] Removing pending post:', postId);
}

