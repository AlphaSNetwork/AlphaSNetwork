import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Heart, 
  MessageCircle, 
  Share2, 
  Send, 
  Users, 
  Coins, 
  TrendingUp,
  Search,
  Bell,
  Settings,
  Plus,
  Home,
  User,
  Hash,
  Wallet
} from 'lucide-react'
import {
  MobileNavbar,
  MobileSidebar,
  MobileBottomNav,
  MobilePostCard,
  MobilePostComposer,
  MobileSearch,
  useSwipeGesture
} from './components/MobileOptimized.jsx'
import './App.css'

function App() {
  const [posts, setPosts] = useState([])
  const [newPost, setNewPost] = useState('')
  const [isMobile, setIsMobile] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('home')
  const [user, setUser] = useState({
    id: 'user_001',
    name: 'Alpha用户',
    username: '@alpha_user',
    avatar: '',
    balance: 1250,
    followers: 342,
    following: 128
  })
  const [stats, setStats] = useState({
    totalUsers: 15420,
    totalPosts: 89650,
    totalTransactions: 234567,
    alphaPrice: 0.85
  })

  // 检测设备类型
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // 模拟获取动态数据
  useEffect(() => {
    const mockPosts = [
      {
        id: 1,
        author: {
          name: 'Alice Chen',
          username: '@alice_crypto',
          avatar: ''
        },
        content: '刚刚体验了Alpha区块链的智能合约功能，去中心化社交的未来就在这里！🚀 #AlphaNetwork #Web3',
        timestamp: '2小时前',
        likes: 42,
        comments: 8,
        shares: 12,
        isLiked: false,
        tags: ['AlphaNetwork', 'Web3']
      },
      {
        id: 2,
        author: {
          name: 'Bob Wilson',
          username: '@bob_dev',
          avatar: ''
        },
        content: '正在开发基于Alpha区块链的DeFi应用，AlphaCoin的经济模型设计得非常巧妙。期待看到更多创新应用！',
        timestamp: '4小时前',
        likes: 67,
        comments: 15,
        shares: 23,
        isLiked: true,
        tags: ['DeFi', 'AlphaCoin']
      },
      {
        id: 3,
        author: {
          name: 'Carol Zhang',
          username: '@carol_artist',
          avatar: ''
        },
        content: '在Alpha网络上发布了我的第一个NFT作品！去中心化让艺术家真正拥有自己的创作。感谢这个平台给予创作者的自由！🎨',
        timestamp: '6小时前',
        likes: 89,
        comments: 24,
        shares: 31,
        isLiked: false,
        tags: ['NFT', 'Art']
      }
    ]
    setPosts(mockPosts)
  }, [])

  const handlePostSubmit = () => {
    if (newPost.trim()) {
      const post = {
        id: posts.length + 1,
        author: {
          name: user.name,
          username: user.username,
          avatar: user.avatar
        },
        content: newPost,
        timestamp: '刚刚',
        likes: 0,
        comments: 0,
        shares: 0,
        isLiked: false,
        tags: []
      }
      setPosts([post, ...posts])
      setNewPost('')
    }
  }

  const handleLike = (postId) => {
    setPosts(posts.map(post => 
      post.id === postId 
        ? { 
            ...post, 
            isLiked: !post.isLiked,
            likes: post.isLiked ? post.likes - 1 : post.likes + 1
          }
        : post
    ))
  }

  // 滑动手势处理
  const swipeGesture = useSwipeGesture(
    () => {
      // 左滑 - 打开菜单
      if (isMobile && !isMenuOpen) {
        setIsMenuOpen(true)
      }
    },
    () => {
      // 右滑 - 关闭菜单
      if (isMobile && isMenuOpen) {
        setIsMenuOpen(false)
      }
    }
  )

  // 移动端渲染
  if (isMobile) {
    return (
      <div 
        className="min-h-screen bg-gray-50"
        {...swipeGesture}
      >
        {/* 移动端导航栏 */}
        <MobileNavbar 
          user={user}
          onMenuToggle={() => setIsMenuOpen(!isMenuOpen)}
          isMenuOpen={isMenuOpen}
        />

        {/* 移动端侧边栏 */}
        <MobileSidebar 
          isOpen={isMenuOpen}
          onClose={() => setIsMenuOpen(false)}
          user={user}
          stats={stats}
        />

        {/* 主内容区 */}
        <div className="pb-16">
          {activeTab === 'home' && (
            <div>
              {/* 发布组件 */}
              <MobilePostComposer 
                user={user}
                newPost={newPost}
                setNewPost={setNewPost}
                onSubmit={handlePostSubmit}
              />
              
              {/* 动态流 */}
              <div>
                {posts.map((post) => (
                  <MobilePostCard 
                    key={post.id}
                    post={post}
                    onLike={handleLike}
                  />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'search' && <MobileSearch />}

          {activeTab === 'post' && (
            <div className="p-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex space-x-4">
                    <Avatar className="w-12 h-12">
                      <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                        {user.name.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <Textarea
                        placeholder="分享你的想法..."
                        value={newPost}
                        onChange={(e) => setNewPost(e.target.value)}
                        className="border-0 bg-gray-50 focus:bg-white transition-colors resize-none"
                        rows={6}
                      />
                      <div className="flex justify-between items-center mt-4">
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm">
                            <Hash className="w-4 h-4 mr-1" />
                            话题
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Plus className="w-4 h-4 mr-1" />
                            媒体
                          </Button>
                        </div>
                        <Button 
                          onClick={() => {
                            handlePostSubmit()
                            setActiveTab('home')
                          }}
                          disabled={!newPost.trim()}
                          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                        >
                          <Send className="w-4 h-4 mr-2" />
                          发布
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="p-4">
              <Card>
                <CardContent className="p-6 text-center">
                  <Bell className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="font-semibold mb-2">暂无新通知</h3>
                  <p className="text-gray-500 text-sm">当有人关注你或与你的内容互动时，通知会显示在这里</p>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="p-4">
              <Card className="mb-4">
                <CardContent className="p-6 text-center">
                  <Avatar className="w-20 h-20 mx-auto mb-4">
                    <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xl">
                      {user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="font-semibold text-lg">{user.name}</h3>
                  <p className="text-gray-500 text-sm mb-4">{user.username}</p>
                  <div className="flex justify-center space-x-6 mb-4">
                    <div className="text-center">
                      <div className="font-semibold text-lg">{user.followers}</div>
                      <div className="text-gray-500 text-sm">关注者</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-lg">{user.following}</div>
                      <div className="text-gray-500 text-sm">关注中</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-center space-x-2 bg-gray-50 rounded-full px-4 py-2">
                    <Wallet className="w-5 h-5 text-blue-600" />
                    <span className="font-medium">{user.balance} ALC</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <Button variant="ghost" className="w-full justify-start">
                      <Settings className="w-5 h-5 mr-3" />
                      设置
                    </Button>
                    <Button variant="ghost" className="w-full justify-start">
                      <Wallet className="w-5 h-5 mr-3" />
                      钱包管理
                    </Button>
                    <Button variant="ghost" className="w-full justify-start">
                      <TrendingUp className="w-5 h-5 mr-3" />
                      数据统计
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* 移动端底部导航栏 */}
        <MobileBottomNav 
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>
    )
  }

  // 桌面端渲染（原有代码）
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* 导航栏 */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">α</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Alpha Social
              </span>
            </div>

            {/* 搜索栏 */}
            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input 
                  placeholder="搜索用户、内容或话题..." 
                  className="pl-10 bg-gray-50 border-0 focus:bg-white transition-colors"
                />
              </div>
            </div>

            {/* 右侧菜单 */}
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="w-5 h-5" />
              </Button>
              <div className="flex items-center space-x-2 bg-gray-50 rounded-full px-3 py-1">
                <Wallet className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium">{user.balance} ALC</span>
              </div>
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                  {user.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* 左侧边栏 */}
          <div className="lg:col-span-1">
            <Card className="mb-6 border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="text-center">
                  <Avatar className="w-20 h-20 mx-auto mb-4">
                    <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xl">
                      {user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <h3 className="font-semibold text-lg">{user.name}</h3>
                  <p className="text-gray-500 text-sm">{user.username}</p>
                  <div className="flex justify-center space-x-4 mt-4 text-sm">
                    <div className="text-center">
                      <div className="font-semibold">{user.followers}</div>
                      <div className="text-gray-500">关注者</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold">{user.following}</div>
                      <div className="text-gray-500">关注中</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 网络统计 */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                  网络统计
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">总用户数</span>
                  <span className="font-semibold">{stats.totalUsers.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">总帖子数</span>
                  <span className="font-semibold">{stats.totalPosts.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">总交易数</span>
                  <span className="font-semibold">{stats.totalTransactions.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ALC价格</span>
                  <span className="font-semibold text-green-600">${stats.alphaPrice}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 主内容区 */}
          <div className="lg:col-span-2">
            {/* 发布新动态 */}
            <Card className="mb-6 border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="flex space-x-4">
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                      {user.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <Textarea
                      placeholder="分享你的想法..."
                      value={newPost}
                      onChange={(e) => setNewPost(e.target.value)}
                      className="border-0 bg-gray-50 focus:bg-white transition-colors resize-none"
                      rows={3}
                    />
                    <div className="flex justify-between items-center mt-4">
                      <div className="flex space-x-2">
                        <Button variant="ghost" size="sm">
                          <Hash className="w-4 h-4 mr-1" />
                          话题
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Plus className="w-4 h-4 mr-1" />
                          媒体
                        </Button>
                      </div>
                      <Button 
                        onClick={handlePostSubmit}
                        disabled={!newPost.trim()}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                      >
                        <Send className="w-4 h-4 mr-2" />
                        发布
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 动态流 */}
            <div className="space-y-6">
              {posts.map((post) => (
                <Card key={post.id} className="border-0 shadow-lg bg-white/70 backdrop-blur-sm hover:shadow-xl transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex space-x-4">
                      <Avatar className="w-10 h-10">
                        <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                          {post.author.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-semibold">{post.author.name}</h4>
                          <span className="text-gray-500 text-sm">{post.author.username}</span>
                          <span className="text-gray-400 text-sm">·</span>
                          <span className="text-gray-500 text-sm">{post.timestamp}</span>
                        </div>
                        <p className="text-gray-800 mb-3 leading-relaxed">{post.content}</p>
                        
                        {/* 标签 */}
                        {post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-4">
                            {post.tags.map((tag, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                #{tag}
                              </Badge>
                            ))}
                          </div>
                        )}

                        {/* 互动按钮 */}
                        <div className="flex items-center space-x-6 text-gray-500">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleLike(post.id)}
                            className={`hover:text-red-500 ${post.isLiked ? 'text-red-500' : ''}`}
                          >
                            <Heart className={`w-4 h-4 mr-1 ${post.isLiked ? 'fill-current' : ''}`} />
                            {post.likes}
                          </Button>
                          <Button variant="ghost" size="sm" className="hover:text-blue-500">
                            <MessageCircle className="w-4 h-4 mr-1" />
                            {post.comments}
                          </Button>
                          <Button variant="ghost" size="sm" className="hover:text-green-500">
                            <Share2 className="w-4 h-4 mr-1" />
                            {post.shares}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* 右侧边栏 */}
          <div className="lg:col-span-1">
            {/* 热门话题 */}
            <Card className="mb-6 border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Hash className="w-5 h-5 mr-2 text-purple-600" />
                  热门话题
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { tag: 'AlphaNetwork', posts: '1.2k 帖子' },
                  { tag: 'Web3', posts: '856 帖子' },
                  { tag: 'DeFi', posts: '634 帖子' },
                  { tag: 'NFT', posts: '423 帖子' },
                  { tag: 'AlphaCoin', posts: '312 帖子' }
                ].map((topic, index) => (
                  <div key={index} className="flex justify-between items-center p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                    <div>
                      <div className="font-medium">#{topic.tag}</div>
                      <div className="text-sm text-gray-500">{topic.posts}</div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* 推荐关注 */}
            <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Users className="w-5 h-5 mr-2 text-blue-600" />
                  推荐关注
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { name: 'Alpha团队', username: '@alpha_team', followers: '12.5k' },
                  { name: 'DeFi专家', username: '@defi_expert', followers: '8.3k' },
                  { name: 'NFT艺术家', username: '@nft_artist', followers: '5.7k' }
                ].map((user, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Avatar className="w-8 h-8">
                        <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm">
                          {user.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium text-sm">{user.name}</div>
                        <div className="text-xs text-gray-500">{user.username}</div>
                      </div>
                    </div>
                    <Button size="sm" variant="outline" className="text-xs">
                      关注
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

