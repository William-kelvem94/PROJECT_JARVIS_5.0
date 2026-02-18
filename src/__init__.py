"""Jarvis 5.0 - Pacote Principal"""

# 🛡️ GLOBAL MONKEY PATCH: OpenVINO compatibility
# NOTE: importing OpenVINO at package import time can be heavy and causes
# multiprocessing child-spawn to hang on Windows (import side-effects).
# Apply the compatibility shim lazily and only within the main process.
try:
    import sys
    import multiprocessing

    if multiprocessing.current_process().name == "MainProcess":
        try:
            import openvino  # type: ignore

            # 1. Patch Node (OpenVINO runtime differences)
            node_obj = getattr(openvino, "Node", None)
            if not node_obj and "openvino.runtime" in sys.modules:
                node_obj = getattr(sys.modules["openvino.runtime"], "Node", None)

            if node_obj and not hasattr(openvino, "Node"):
                openvino.Node = node_obj

            # 2. Patch op module
            op_obj = getattr(openvino, "op", None)
            if not op_obj and "openvino.runtime" in sys.modules:
                op_obj = getattr(sys.modules["openvino.runtime"], "op", None)

            if op_obj:
                sys.modules["openvino.op"] = op_obj
                if not hasattr(openvino, "op"):
                    openvino.op = op_obj
        except Exception:
            # If OpenVINO isn't available or fails, silently continue.
            pass
except Exception:
    # If multiprocessing isn't available or any unexpected error occurs,
    # continue without applying the shim.
    pass

# NumPy 2.0 compatibility shim: some downstream libs still reference removed
# aliases like np.float_, np.int_, np.uint. Add safe aliases if missing.
try:
    import numpy as _np

    if not hasattr(_np, "float_"):
        _np.float_ = _np.float64
    if not hasattr(_np, "int_"):
        _np.int_ = _np.int64
    if not hasattr(_np, "uint"):
        _np.uint = _np.uint64
except Exception:
    pass
