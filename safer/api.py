from requests import Session

SAFER_KEYWORD_URL = 'https://safer.fmcsa.dot.gov/keywordx.asp'
SAFER_QUERY_URL = 'https://safer.fmcsa.dot.gov/query.asp'

sess = Session()
sess.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'safer.fmcsa.dot.gov',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
})


def api_call_search(query):
    r = sess.get(url=SAFER_KEYWORD_URL, params={
        'searchstring': '*{}*'.format(query.upper()),
        'SEARCHTYPE': ''
    })

    return r


def api_call_get_usdot(usdot):
    r = sess.post(url=SAFER_QUERY_URL, data={
        'searchType': 'ANY',
        'query_type': 'queryCarrierSnapshot',
        'query_param': 'USDOT',
        'query_string': usdot
    })
    return r


def api_call_get_mcmx(mcmx):
    r = sess.post(url=SAFER_QUERY_URL, data={
        'searchType': 'ANY',
        'query_type': 'queryCarrierSnapshot',
        'query_param': 'MC_MX',
        'query_string': mcmx
    })
    return r
