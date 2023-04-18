pip3 install -r requirements.txt

you have to change the headers in this file for it to work:
(pip installation path)

lib/python/site-packages/pysbr/queries/query.py

```
headers = {
    "User-Agent": ua.random,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, /",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "site-domain": "bmrodds-com",
    "origin": "https://www.bookmakersreview.com/",
    "referer": "https://www.bookmakersreview.com/"
}
transport = RequestsHTTPTransport(
    url="https://ms.production-us-east-1.bookmakersreview.com/ms-odds-v2/odds-v2-service",
    headers=headers,
)
```