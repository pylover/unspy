import requests


def request(verb, url='/', form=None, query=None):
    kw = {}
    headers = kw.setdefault('headers', {})

    if form:
        kw['data'] = form

    if query:
        kw['params'] = query

    if form:
        kw['data'] = form

    response = requests.request(verb, url, **kw)

    return response
