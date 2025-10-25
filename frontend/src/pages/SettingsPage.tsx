import { useState } from 'react'
import { Settings as SettingsIcon, User, Lock, Save } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { userApi } from '@/lib/api'
import { toast } from '@/components/ui/toaster'

const SettingsPage = () => {
  const { user, updateUser } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  
  const [formData, setFormData] = useState({
    email: user?.email || '',
    full_name: user?.full_name || '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const updateData: any = {
        email: formData.email,
        full_name: formData.full_name,
      }

      if (formData.password) {
        updateData.password = formData.password
      }

      const response = await userApi.updateMe(updateData)
      updateUser(response.data)
      
      toast({ message: 'Configurações salvas com sucesso!', type: 'success' })
      setFormData({ ...formData, password: '' })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao salvar configurações'
      toast({ message, type: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <SettingsIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-200">Configurações</h1>
            <p className="text-gray-400">Gerencie sua conta e preferências</p>
          </div>
        </div>

        {/* User Info Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8"
        >
          <div className="flex items-center gap-4 mb-6">
            <User className="w-6 h-6 text-primary-400" />
            <h2 className="text-xl font-semibold text-gray-200">
              Informações do Perfil
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="label">Nome de Usuário</label>
              <input
                id="username"
                type="text"
                value={user?.username || ''}
                className="input"
                disabled
                title="Nome de usuário (não pode ser alterado)"
              />
              <p className="text-sm text-gray-500 mt-1">
                O nome de usuário não pode ser alterado
              </p>
            </div>

            <div>
              <label htmlFor="email" className="label">Email</label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input"
                required
                title="Seu endereço de email"
              />
            </div>

            <div>
              <label htmlFor="fullname" className="label">Nome Completo</label>
              <input
                id="fullname"
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="input"
                title="Seu nome completo"
              />
            </div>

            <div className="pt-4 border-t border-dark-800">
              <div className="flex items-center gap-4 mb-4">
                <Lock className="w-6 h-6 text-primary-400" />
                <h3 className="text-lg font-semibold text-gray-200">
                  Alterar Senha
                </h3>
              </div>

              <div>
                <label htmlFor="password" className="label">Nova Senha</label>
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="input"
                  placeholder="Deixe em branco para não alterar"
                  title="Nova senha (mínimo 8 caracteres)"
                  minLength={8}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Mínimo de 8 caracteres
                </p>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 disabled:opacity-50"
            >
              {isLoading ? 'Salvando...' : 'Salvar Alterações'}
              <Save className="w-5 h-5" />
            </button>
          </form>
        </motion.div>

        {/* System Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-200 mb-4">
            Informações do Sistema
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Versão</span>
              <span className="text-gray-200 font-medium">3.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Ambiente</span>
              <span className="text-gray-200 font-medium">Production</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">ID do Usuário</span>
              <span className="text-gray-200 font-mono text-xs">{user?.id}</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default SettingsPage

