import requests


def request(verb, url='/', form=None, query=None, files=None):
    kw = {}
    # headers = kw.setdefault('headers', {})

    if form:
        kw['data'] = form

    if query:
        kw['params'] = query

    if files:
        kw['files'] = files

    response = requests.request(verb, url, **kw)

    return response
