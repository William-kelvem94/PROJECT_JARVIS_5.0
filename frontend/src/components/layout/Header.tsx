import { useNavigate } from 'react-router-dom'
import { LogOut, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { toast } from '@/components/ui/toaster'

const Header = () => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authApi.logout()
      logout()
      navigate('/login')
      toast({ message: 'Logout realizado com sucesso', type: 'success' })
    } catch (error) {
      console.error('Logout error:', error)
      logout()
      navigate('/login')
    }
  }

  return (
    <header className="h-16 glass border-b border-dark-800 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-gray-200">
          Bem-vindo, {user?.username || 'Usuário'}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        {/* User menu */}
        <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-dark-800 border border-dark-700">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="text-sm">
            <p className="font-medium text-gray-200">{user?.username}</p>
            <p className="text-xs text-gray-400">{user?.email}</p>
          </div>
        </div>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="btn-ghost p-2"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}

export default Header

