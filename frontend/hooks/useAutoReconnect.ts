import { useEffect, useRef } from 'react';
import { RoomEvent } from 'livekit-client';
import { log } from '@/lib/logger';

export function useAutoReconnect(session: any) {
  const { room, connect } = session;
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!room) return;

    const handleDisconnected = async () => {
      log.info('🔌 Conexão perdida. Tentando reconectar em 2s...');

      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(async () => {
        try {
          log.info('🔄 Iniciando reconexão automática...');
          // @ts-ignore: connect fn might not be in type def but exists in runtime
          if (typeof connect === 'function') {
            await connect();
            log.info('✅ Reconectado com sucesso!');
          } else {
            log.warn('⚠️ Função connect não encontrada na sessão.');
            location.reload(); // Fallback bravo: reload na página
          }
        } catch (error) {
          log.error('❌ Falha ao reconectar:', error);
          // Se falhar, o evento de disconnect pode não disparar de novo se já estiver desconectado.
          // Em um sistema robusto, poderíamos ter um loop de retry aqui,
          // mas o useSession muitas vezes reseta o estado.
          // Por enquanto, uma tentativa simples resolve resets do backend.
        }
      }, 2000);
    };

    room.on(RoomEvent.Disconnected, handleDisconnected);

    return () => {
      room.off(RoomEvent.Disconnected, handleDisconnected);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [room, connect]);
}
