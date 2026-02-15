import importlib,traceback
pkgs=['dlib','face_recognition','tkinter_tooltip']
for p in pkgs:
    try:
        m=importlib.import_module(p)
        print(p,'OK', getattr(m,'__version__',''))
    except Exception as e:
        print(p,'ERROR')
        traceback.print_exc()
