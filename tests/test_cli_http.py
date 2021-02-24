# uns http get home.nodemcu/foo
# uns http set home.nodemcu 1
# uns http set home.nodemcu foo=bar baz="qux quux"
# uns http set home.nodemcu foo=@bar.ext


def test_http_get(socketclass_mock, requests_mock, httpcli):
    httpcli('foo.com')
    requests_mock.request.assert_called_with('GET', '10.0.0.2')

    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
    sock.sendto.assert_called_once_with(b'\x01foo.com', mock.ANY)
    sock.recvfrom.assert_called_once()
