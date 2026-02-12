"""Jarvis 5.0 - Pacote Principal"""

# 🛡️ GLOBAL MONKEY PATCH: Correção Crítica para OpenVINO/Optimum-Intel
# Previne erro 'module openvino has no attribute Node' e 'No module named openvino.op'
try:
    import sys
    import openvino
    import openvino.runtime
    # 1. Patch Node
    node_obj = getattr(openvino.runtime, 'Node', None)
    if node_obj:
        if not hasattr(openvino, 'Node'): openvino.Node = node_obj
        if not hasattr(openvino.runtime, 'Node'): openvino.runtime.Node = node_obj
    
    # 2. Patch op module
    if hasattr(openvino.runtime, 'op'):
        sys.modules['openvino.op'] = openvino.runtime.op
        if not hasattr(openvino, 'op'): openvino.op = openvino.runtime.op
except Exception:
    pass
