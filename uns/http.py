import requests


def request(verb, url='/', form=None, query=None, files=None, headers=None,
            **kwargs):
    kw = {}

    if form:
        kw['data'] = form

    if query:
        kw['params'] = query

    if files:
        kw['files'] = files

    if headers:
        kw['headers'] = headers

    kw.update(kwargs)

    response = requests.request(verb, url, **kw)

    return response
