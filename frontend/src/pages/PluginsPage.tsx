import { useEffect, useState } from 'react'
import { Puzzle, Power, PowerOff, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'
import { pluginApi } from '@/lib/api'
import { toast } from '@/components/ui/toaster'

interface Plugin {
  name: string
  version: string
  description: string
  author: string
  enabled: boolean
  initialized: boolean
}

const PluginsPage = () => {
  const [plugins, setPlugins] = useState<Plugin[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadPlugins()
  }, [])

  const loadPlugins = async () => {
    try {
      const response = await pluginApi.list()
      setPlugins(response.data)
    } catch (error) {
      toast({ message: 'Erro ao carregar plugins', type: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  const togglePlugin = async (name: string, enabled: boolean) => {
    try {
      if (enabled) {
        await pluginApi.disable(name)
      } else {
        await pluginApi.enable(name)
      }
      await loadPlugins()
      toast({
        message: `Plugin ${enabled ? 'desativado' : 'ativado'} com sucesso`,
        type: 'success',
      })
    } catch (error) {
      toast({ message: 'Erro ao alterar status do plugin', type: 'error' })
    }
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <RefreshCw className="w-8 h-8 text-primary-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <Puzzle className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-200">Plugins</h1>
            <p className="text-gray-400">
              Gerencie os plugins do sistema
            </p>
          </div>
        </div>

        {/* Plugins Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plugins.map((plugin, index) => (
            <motion.div
              key={plugin.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card p-6 space-y-4"
            >
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-200 capitalize">
                    {plugin.name}
                  </h3>
                  <p className="text-sm text-gray-400">v{plugin.version}</p>
                </div>
                <div
                  className={`w-3 h-3 rounded-full ${
                    plugin.enabled && plugin.initialized
                      ? 'bg-green-500'
                      : 'bg-gray-600'
                  }`}
                  title={
                    plugin.enabled && plugin.initialized ? 'Ativo' : 'Inativo'
                  }
                />
              </div>

              {/* Description */}
              <p className="text-sm text-gray-400">{plugin.description}</p>

              {/* Author */}
              <p className="text-xs text-gray-500">Por {plugin.author}</p>

              {/* Actions */}
              <div className="pt-4 border-t border-dark-800">
                <button
                  onClick={() => togglePlugin(plugin.name, plugin.enabled)}
                  className={`btn w-full ${
                    plugin.enabled ? 'btn-secondary' : 'btn-primary'
                  }`}
                >
                  {plugin.enabled ? (
                    <>
                      <PowerOff className="w-4 h-4" />
                      <span>Desativar</span>
                    </>
                  ) : (
                    <>
                      <Power className="w-4 h-4" />
                      <span>Ativar</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Empty state */}
        {plugins.length === 0 && (
          <div className="text-center py-12">
            <Puzzle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              Nenhum plugin encontrado
            </h3>
            <p className="text-gray-500">
              Adicione plugins ao diretório backend/app/plugins
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default PluginsPage

