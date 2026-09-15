"""Small synchronous SDK for the stable Platform API."""
import base64, uuid, httpx
class SimorghError(Exception):
    def __init__(self,status_code,code,message,request_id=None): super().__init__(message); self.status_code=status_code; self.code=code; self.request_id=request_id
class SimorghClient:
    def __init__(self,key,secret,base_url='http://localhost:8000',timeout=30): self.key=key;self.secret=secret;self.base_url=base_url.rstrip('/');self.timeout=timeout;self.token=None
    def _request(self,method,path,**kwargs):
        headers=kwargs.pop('headers',{});headers.setdefault('X-Request-ID',str(uuid.uuid4()))
        response=httpx.request(method,self.base_url+path,headers=headers,timeout=self.timeout,**kwargs)
        if response.status_code>=400:
            err=response.json().get('error',{});raise SimorghError(response.status_code,err.get('code','HTTP_ERROR'),err.get('message','Request failed'),err.get('request_id'))
        return response.json(),response.headers.get('X-Request-ID')
    def authenticate(self):
        basic=base64.b64encode(f'{self.key}:{self.secret}'.encode()).decode();data,_=self._request('POST','/api/v1/auth/token',headers={'Authorization':f'Basic {basic}'}) ;self.token=data['data']['access_token'];return self.token
    def _auth_headers(self):
        if not self.token:self.authenticate()
        return {'Authorization':f'Bearer {self.token}'}
    def chat(self,model,messages,**kwargs): return self._request('POST','/api/v1/ai/chat',headers=self._auth_headers(),json={'model':model,'messages':messages,**kwargs})[0]
    def embeddings(self,model,input,**kwargs): return self._request('POST','/api/v1/ai/embeddings',headers=self._auth_headers(),json={'model':model,'input':input,**kwargs})[0]
    def health(self): return self._request('GET','/health')[0]
    def ready(self): return self._request('GET','/ready')[0]
