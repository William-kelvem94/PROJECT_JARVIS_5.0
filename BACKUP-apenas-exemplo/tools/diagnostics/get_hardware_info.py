import platform, psutil, multiprocessing, subprocess
info = {
    'platform': platform.platform(),
    'processor': platform.processor(),
    'cpu_cores_physical': psutil.cpu_count(logical=False),
    'cpu_cores_logical': multiprocessing.cpu_count(),
    'total_ram_gb': round(psutil.virtual_memory().total / (1024**3), 2),
}
try:
    import torch
    info['torch_cuda_available'] = torch.cuda.is_available()
    info['gpu_name'] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'
except:
    info['torch'] = 'Não instalado ou erro'
try:
    smi = subprocess.run(['nvidia-smi', '-L'], capture_output=True, text=True)
    info['nvidia_smi'] = smi.stdout.strip() or 'No NVIDIA'
except:
    info['nvidia_smi'] = 'Não detectado'
print(info)
