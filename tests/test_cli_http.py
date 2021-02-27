from unittest import mock

# uns http get home.nodemcu/foo
# uns http set home.nodemcu 1
# uns http set home.nodemcu foo=bar baz="qux quux"
# uns http set home.nodemcu foo=@bar.ext


def test_http(socketclass_mock, requests_mock, dbfile_mock, httpcli):
    s, o, e = httpcli('get', 'foo.com')
    assert e == ''
    assert o == 'bar'
    assert s == 0
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_called_once()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()
    requests_mock.assert_called_with('GET', 'http://10.0.0.2')

    s, o, e = httpcli('get', 'foo.com/bar')
    assert s == 0
    requests_mock.assert_called_with('GET', 'http://10.0.0.2/bar')

    s, o, e = httpcli('set', 'foo.com', '1')
    assert s == 0
    requests_mock.assert_called_with('SET', 'http://10.0.0.2', data='1')

    s, o, e = httpcli('set', 'foo.com', 'bar=baz', '?qux=quux')
    assert s == 0
    requests_mock.assert_called_with(
        'SET', 'http://10.0.0.2',
        data=[('bar', 'baz')],
        params=[('qux', 'quux')]
    )

    s, o, e = httpcli('set', 'foo.com', '@bar=baz.txt')
    assert s == 0
    requests_mock.assert_called_with(
        'SET', 'http://10.0.0.2',
        files=[('bar', 'baz.txt')],
    )

    requests_mock.return_value.status_code = 400
    s, o, e = httpcli('get', 'foo.com')
    assert s == 1


def test_http_binary_response(socketclass_mock, requests_mock, dbfile_mock,
                              httpcli_binary):
    response = requests_mock.return_value
    response.content = b'foo bar baz'
    response.headers['content-type'] = 'image/jpeg'
    s, o, e = httpcli_binary('get', 'foo.com')
    assert s == 0
    assert e == ''
    assert o == b'foo bar baz'


def test_http_port(socketclass_mock, requests_mock, dbfile_mock, httpcli):
    s, o, e = httpcli('-p8080', 'get', 'foo.com/bar')
    assert s == 0
    requests_mock.assert_called_with('GET', 'http://10.0.0.2:8080/bar')
