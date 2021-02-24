import requests


def request(verb, url='/', form=None, query=None):
    kw = {}
    headers = {}

    if form:
        kw['data'] = form

    kw['headers'] = headers
    response = requests.request(
        verb.upper(),
        url,
        **kw
    )

    return response
