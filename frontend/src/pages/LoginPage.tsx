import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Zap, LogIn } from 'lucide-react'
import { motion } from 'framer-motion'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { toast } from '@/components/ui/toaster'

const LoginPage = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await authApi.login(formData)
      const { access_token, refresh_token } = response.data

      // Get user info
      const userResponse = await authApi.getMe()
      
      setAuth(userResponse.data, access_token, refresh_token)
      toast({ message: 'Login realizado com sucesso!', type: 'success' })
      navigate('/')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao fazer login'
      toast({ message, type: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="card p-8 space-y-8">
          {/* Logo */}
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 glow">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gradient">JARVIS</h1>
              <p className="text-gray-400 mt-2">AI Assistant v3.0</p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="label">Usuário</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="input"
                placeholder="Digite seu usuário"
                required
              />
            </div>

            <div>
              <label className="label">Senha</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="input"
                placeholder="Digite sua senha"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 text-lg disabled:opacity-50"
            >
              {isLoading ? 'Entrando...' : 'Entrar'}
              <LogIn className="w-5 h-5" />
            </button>
          </form>

          {/* Register link */}
          <div className="text-center text-sm text-gray-400">
            Não tem uma conta?{' '}
            <Link to="/register" className="text-primary-400 hover:text-primary-300">
              Registre-se
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default LoginPage

