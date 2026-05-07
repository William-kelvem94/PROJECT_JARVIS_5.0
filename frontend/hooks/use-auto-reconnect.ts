import { useEffect, useRef } from 'react';
import { log } from '@/lib/logger';

export function useAutoReconnect(session: any) {
  const { room, connect } = session;
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!room) return;

    const handleDisconnected = async () => {
      log.info('🔌 Conexão perdida. Tentando reconectar em 2s...');

      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(async () => {
        if (!mountedRef.current) return;
        try {
          log.info('🔄 Iniciando reconexão automática...');
          if (typeof connect === 'function') {
            await connect();
            log.info('✅ Reconectado com sucesso!');
          } else {
            log.warn('⚠️ Função connect não encontrada na sessão.');
            location.reload();
          }
        } catch (error) {
          log.error('❌ Falha ao reconectar:', error);
        }
      }, 2000);
    };

    if (typeof room.on === 'function') {
      room.on('disconnected', handleDisconnected);
    }

    return () => {
      if (typeof room.off === 'function') {
        room.off('disconnected', handleDisconnected);
      }
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [room, connect]);
}
