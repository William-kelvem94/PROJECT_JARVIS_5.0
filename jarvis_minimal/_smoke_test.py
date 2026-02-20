from jarvis_minimal.agent import JarvisAgent

agent = JarvisAgent()
print('Sending test 1...')
agent.handle_command('teste: diga olá')
print('Sending test 2...')
agent.handle_command('teste: repita a última resposta')
print('Done')
