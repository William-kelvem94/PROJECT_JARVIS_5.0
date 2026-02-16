# -*- coding: utf-8 -*-
import sys
import os
import threading
sys.path.insert(0, 'src')

def start_web_server():
    from web.web_server import start_server
    import asyncio
    import uvicorn
    async def run_server():
        config = uvicorn.Config('web.web_server:app', host='localhost', port=5000, log_level='warning')
        server = uvicorn.Server(config)
        await server.serve()
    asyncio.run(run_server())

web_thread = threading.Thread(target=start_web_server, daemon=True)
web_thread.start()

print('🌐 Dashboard iniciado em: http://localhost:5000')
print('📊 Abra seu navegador e veja os logs em tempo real!')
print('')
print('🚀 Iniciando treinamento sobre Inteligência Artificial...')
print('')
print('=' * 60)

os.system('python scripts/training/external_trainer.py --component study --topic "Inteligência Artificial" --config config/training_config.yaml')
