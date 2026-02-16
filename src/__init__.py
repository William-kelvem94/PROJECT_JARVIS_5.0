"""Jarvis 5.0 - Pacote Principal"""

# ðŸ›¡ï¸ GLOBAL MONKEY PATCH: CorreÃ§Ã£o CrÃ­tica para OpenVINO/Optimum-Intel
# Previne erro 'module openvino has no attribute Node' e 'No module named openvino.op'
try:
    import sys
    import openvino  # type: ignore
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

# NumPy 2.0 compatibility shim: some downstream libs still reference removed
# aliases like np.float_, np.int_, np.uint. Add safe aliases if missing.
try:
    import numpy as _np
    if not hasattr(_np, 'float_'):
        _np.float_ = _np.float64
    if not hasattr(_np, 'int_'):
        _np.int_ = _np.int64
    if not hasattr(_np, 'uint'):
        _np.uint = _np.uint64
except Exception:
    pass
