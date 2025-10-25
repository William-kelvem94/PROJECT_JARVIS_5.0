import { useNavigate } from 'react-router-dom'
import { MessageSquare, Zap, Shield, Puzzle } from 'lucide-react'
import { motion } from 'framer-motion'

const HomePage = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: MessageSquare,
      title: 'Chat Inteligente',
      description: 'Conversas naturais com IA local usando Ollama',
    },
    {
      icon: Zap,
      title: 'Respostas Rápidas',
      description: 'Streaming em tempo real via WebSocket',
    },
    {
      icon: Shield,
      title: 'Privacidade Total',
      description: 'Seus dados ficam em seu servidor local',
    },
    {
      icon: Puzzle,
      title: 'Sistema de Plugins',
      description: 'Voice, DeepSeek, Alexa e muito mais',
    },
  ]

  return (
    <div className="min-h-full flex items-center justify-center p-8">
      <div className="max-w-6xl w-full space-y-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6"
        >
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 glow animate-float">
            <Zap className="w-12 h-12 text-white" />
          </div>

          <h1 className="text-6xl font-bold">
            <span className="text-gradient">JARVIS</span>
            <span className="text-gray-200"> AI Assistant</span>
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Assistente de IA conversacional completo com arquitetura de plugins,
            integração local e streaming em tempo real
          </p>

          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => navigate('/chat')}
              className="btn-primary text-lg px-8 py-4"
            >
              Iniciar Conversa
              <MessageSquare className="w-5 h-5" />
            </button>
            <button
              onClick={() => navigate('/plugins')}
              className="btn-secondary text-lg px-8 py-4"
            >
              Ver Plugins
              <Puzzle className="w-5 h-5" />
            </button>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="card p-6 hover:border-primary-600 transition-all cursor-pointer glow-hover"
            >
              <div className="w-12 h-12 rounded-lg bg-primary-600/20 flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-200 mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <div className="glass rounded-2xl p-8 border border-dark-800">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-gradient mb-2">100%</div>
              <div className="text-gray-400">Local & Privado</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gradient mb-2">3+</div>
              <div className="text-gray-400">Plugins Ativos</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-gradient mb-2">∞</div>
              <div className="text-gray-400">Possibilidades</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage

