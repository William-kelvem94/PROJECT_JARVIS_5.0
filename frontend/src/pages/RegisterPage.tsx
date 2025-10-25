import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Zap, UserPlus } from 'lucide-react'
import { motion } from 'framer-motion'
import { authApi } from '@/lib/api'
import { toast } from '@/components/ui/toaster'

const RegisterPage = () => {
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await authApi.register(formData)
      toast({ message: 'Conta criada com sucesso! Faça login.', type: 'success' })
      navigate('/login')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao criar conta'
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
              <h1 className="text-3xl font-bold text-gradient">Criar Conta</h1>
              <p className="text-gray-400 mt-2">Junte-se ao JARVIS AI</p>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Usuário</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="input"
                placeholder="Escolha um usuário"
                required
                minLength={3}
              />
            </div>

            <div>
              <label className="label">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <label className="label">Nome Completo (opcional)</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="input"
                placeholder="Seu nome"
              />
            </div>

            <div>
              <label className="label">Senha</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="input"
                placeholder="Mínimo 8 caracteres"
                required
                minLength={8}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 text-lg disabled:opacity-50"
            >
              {isLoading ? 'Criando conta...' : 'Criar Conta'}
              <UserPlus className="w-5 h-5" />
            </button>
          </form>

          {/* Login link */}
          <div className="text-center text-sm text-gray-400">
            Já tem uma conta?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300">
              Faça login
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default RegisterPage

