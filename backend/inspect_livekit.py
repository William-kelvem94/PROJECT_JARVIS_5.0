import livekit
import pkgutil

print('livekit dir', dir(livekit))
print('submodules:', [m.name for m in pkgutil.iter_modules(livekit.__path__)])
try:
    from livekit import jwt
    print('has jwt module', dir(jwt))
except Exception as e:
    print('no jwt module', e)
