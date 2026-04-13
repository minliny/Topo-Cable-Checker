import httpx
import time

client = httpx.Client()
url = "http://localhost:8000/api/baselines"

start = time.time()
res = client.get(url)
print(f"Loading tree took {(time.time() - start)*1000:.2f}ms. Size: {len(res.text)/1024:.2f}KB")
