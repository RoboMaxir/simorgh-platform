import sys
from types import SimpleNamespace
import pytest

@pytest.fixture
def client(monkeypatch):
    fake = SimpleNamespace(request=lambda *a, **kw: None)
    monkeypatch.setitem(sys.modules, 'httpx', fake)
    sys.modules.pop('sdk', None)
    from sdk import SimorghClient
    return SimorghClient('key', 'secret')

def test_sdk_health_request(client, monkeypatch):
    class Response:
        status_code=200; headers={'X-Request-ID':'r'}
        def json(self): return {'status':'healthy'}
    monkeypatch.setattr(sys.modules['httpx'], 'request', lambda *a, **kw: Response())
    assert client.health()=={'status':'healthy'}

def test_sdk_typed_error(client, monkeypatch):
    from sdk import SimorghError
    class Response:
        status_code=401; headers={}
        def json(self): return {'error':{'code':'INVALID_CREDENTIALS','message':'no'}}
    monkeypatch.setattr(sys.modules['httpx'], 'request', lambda *a, **kw: Response())
    with pytest.raises(SimorghError, match='no') as exc: client.health()
    assert exc.value.code=='INVALID_CREDENTIALS'

def test_request_context_scope_is_explicit():
    from app.core.context import RequestContext
    context=RequestContext('r','t','a','i','c',['ai.chat'])
    assert context.has_scope('ai.chat')
    assert not context.has_scope('audit.read')
