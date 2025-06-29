import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Avatar, AvatarFallback } from '@/components/ui/avatar.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Heart, 
  MessageCircle, 
  Share2, 
  Send, 
  Search,
  Bell,
  Settings,
  Plus,
  Home,
  User,
  Hash,
  Wallet,
  Menu,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

// 移动端导航栏组件
export function MobileNavbar({ user, onMenuToggle, isMenuOpen }) {
  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 lg:hidden">
      <div className="flex justify-between items-center h-14 px-4">
        {/* 左侧菜单按钮 */}
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onMenuToggle}
          className="p-2"
        >
          {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </Button>

        {/* 中间Logo */}
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xs">α</span>
          </div>
          <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Alpha
          </span>
        </div>

        {/* 右侧用户头像和余额 */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 bg-gray-50 rounded-full px-2 py-1">
            <Wallet className="w-3 h-3 text-blue-600" />
            <span className="text-xs font-medium">{user.balance}</span>
          </div>
          <Avatar className="w-7 h-7">
            <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs">
              {user.name.charAt(0)}
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </nav>
  )
}

// 移动端侧边栏菜单
export function MobileSidebar({ isOpen, onClose, user, stats }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-40 lg:hidden">
      {/* 背景遮罩 */}
      <div 
        className="fixed inset-0 bg-black/50" 
        onClick={onClose}
      />
      
      {/* 侧边栏内容 */}
      <div className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl transform transition-transform">
        <div className="p-6">
          {/* 用户信息 */}
          <div className="text-center mb-6">
            <Avatar className="w-16 h-16 mx-auto mb-3">
              <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-lg">
                {user.name.charAt(0)}
              </AvatarFallback>
            </Avatar>
            <h3 className="font-semibold text-lg">{user.name}</h3>
            <p className="text-gray-500 text-sm">{user.username}</p>
            <div className="flex justify-center space-x-4 mt-3 text-sm">
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

          {/* 菜单项 */}
          <div className="space-y-2">
            <Button variant="ghost" className="w-full justify-start">
              <Home className="w-5 h-5 mr-3" />
              首页
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Search className="w-5 h-5 mr-3" />
              搜索
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Bell className="w-5 h-5 mr-3" />
              通知
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <MessageCircle className="w-5 h-5 mr-3" />
              消息
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <User className="w-5 h-5 mr-3" />
              个人资料
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="w-5 h-5 mr-3" />
              设置
            </Button>
          </div>

          {/* 网络统计 */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-3 flex items-center">
              <Hash className="w-4 h-4 mr-2" />
              网络统计
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">总用户数</span>
                <span className="font-semibold">{stats.totalUsers.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">ALC价格</span>
                <span className="font-semibold text-green-600">${stats.alphaPrice}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 移动端底部导航栏
export function MobileBottomNav({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'home', icon: Home, label: '首页' },
    { id: 'search', icon: Search, label: '搜索' },
    { id: 'post', icon: Plus, label: '发布' },
    { id: 'notifications', icon: Bell, label: '通知' },
    { id: 'profile', icon: User, label: '我的' }
  ]

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 lg:hidden">
      <div className="flex">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex-1 flex flex-col items-center justify-center py-2 px-1 ${
                isActive 
                  ? 'text-blue-600' 
                  : 'text-gray-500'
              }`}
            >
              <Icon className={`w-5 h-5 mb-1 ${
                tab.id === 'post' 
                  ? 'bg-blue-600 text-white rounded-full p-1 w-6 h-6' 
                  : ''
              }`} />
              <span className="text-xs">{tab.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// 移动端帖子卡片组件
export function MobilePostCard({ post, onLike }) {
  return (
    <Card className="border-0 border-b border-gray-100 rounded-none bg-white">
      <CardContent className="p-4">
        <div className="flex space-x-3">
          <Avatar className="w-10 h-10 flex-shrink-0">
            <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
              {post.author.name.charAt(0)}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h4 className="font-semibold text-sm truncate">{post.author.name}</h4>
              <span className="text-gray-500 text-xs">{post.author.username}</span>
              <span className="text-gray-400 text-xs">·</span>
              <span className="text-gray-500 text-xs">{post.timestamp}</span>
            </div>
            <p className="text-gray-800 text-sm leading-relaxed mb-3">{post.content}</p>
            
            {/* 标签 */}
            {post.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {post.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs px-2 py-1">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* 互动按钮 */}
            <div className="flex items-center justify-between text-gray-500">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onLike(post.id)}
                className={`hover:text-red-500 p-2 ${post.isLiked ? 'text-red-500' : ''}`}
              >
                <Heart className={`w-4 h-4 mr-1 ${post.isLiked ? 'fill-current' : ''}`} />
                <span className="text-xs">{post.likes}</span>
              </Button>
              <Button variant="ghost" size="sm" className="hover:text-blue-500 p-2">
                <MessageCircle className="w-4 h-4 mr-1" />
                <span className="text-xs">{post.comments}</span>
              </Button>
              <Button variant="ghost" size="sm" className="hover:text-green-500 p-2">
                <Share2 className="w-4 h-4 mr-1" />
                <span className="text-xs">{post.shares}</span>
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 移动端发布组件
export function MobilePostComposer({ user, newPost, setNewPost, onSubmit }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <Card className="border-0 border-b border-gray-100 rounded-none bg-white">
      <CardContent className="p-4">
        <div className="flex space-x-3">
          <Avatar className="w-10 h-10 flex-shrink-0">
            <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
              {user.name.charAt(0)}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <Textarea
              placeholder="分享你的想法..."
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              onFocus={() => setIsExpanded(true)}
              className="border-0 bg-transparent resize-none text-lg placeholder:text-gray-500"
              rows={isExpanded ? 4 : 2}
            />
            {isExpanded && (
              <div className="flex justify-between items-center mt-3">
                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm" className="text-blue-600">
                    <Hash className="w-4 h-4 mr-1" />
                    话题
                  </Button>
                  <Button variant="ghost" size="sm" className="text-blue-600">
                    <Plus className="w-4 h-4 mr-1" />
                    媒体
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      setIsExpanded(false)
                      setNewPost('')
                    }}
                  >
                    取消
                  </Button>
                  <Button 
                    onClick={onSubmit}
                    disabled={!newPost.trim()}
                    size="sm"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    发布
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 移动端搜索组件
export function MobileSearch() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  return (
    <div className="p-4">
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <Input 
          placeholder="搜索用户、内容或话题..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-gray-50 border-0 focus:bg-white transition-colors"
        />
      </div>
      
      {/* 热门搜索 */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3">热门搜索</h3>
        <div className="flex flex-wrap gap-2">
          {['AlphaNetwork', 'Web3', 'DeFi', 'NFT', 'AlphaCoin'].map((tag, index) => (
            <Badge key={index} variant="outline" className="cursor-pointer">
              #{tag}
            </Badge>
          ))}
        </div>
      </div>

      {/* 搜索结果 */}
      {searchQuery && (
        <div>
          <h3 className="font-semibold mb-3">搜索结果</h3>
          <div className="text-gray-500 text-center py-8">
            暂无搜索结果
          </div>
        </div>
      )}
    </div>
  )
}

// 触摸手势Hook
export function useSwipeGesture(onSwipeLeft, onSwipeRight) {
  const [touchStart, setTouchStart] = useState(null)
  const [touchEnd, setTouchEnd] = useState(null)

  const minSwipeDistance = 50

  const onTouchStart = (e) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }

  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance

    if (isLeftSwipe && onSwipeLeft) {
      onSwipeLeft()
    }
    if (isRightSwipe && onSwipeRight) {
      onSwipeRight()
    }
  }

  return {
    onTouchStart,
    onTouchMove,
    onTouchEnd
  }
}

