"""Jarvis 5.0 - Pacote Principal"""

# ðŸ›¡ï¸ GLOBAL MONKEY PATCH: CorreÃ§Ã£o CrÃ­tica para OpenVINO/Optimum-Intel
# Previne erro 'module openvino has no attribute Node' e 'No module named openvino.op'
try:
    import sys
    import openvino
    # 1. Patch Node - Favorece topo (OpenVINO 2023.1+)
    node_obj = getattr(openvino, 'Node', None)
    if not node_obj and 'openvino.runtime' in sys.modules:
        node_obj = getattr(sys.modules['openvino.runtime'], 'Node', None)
        
    if node_obj:
        if not hasattr(openvino, 'Node'): openvino.Node = node_obj
    
    # 2. Patch op module
    op_obj = getattr(openvino, 'op', None)
    if not op_obj and 'openvino.runtime' in sys.modules:
        op_obj = getattr(sys.modules['openvino.runtime'], 'op', None)
        
    if op_obj:
        sys.modules['openvino.op'] = op_obj
        if not hasattr(openvino, 'op'): openvino.op = op_obj
except Exception:
    pass
