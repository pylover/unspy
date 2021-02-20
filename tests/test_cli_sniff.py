import functools


def test_cli_resolve_nocache(socketclass_mock, cliapp):
    sniffcli = functools.partial(cliapp, 'sniff')

    sock = socketclass_mock.return_value
    sock.recvfrom.side_effect = [
        (b'\x01foo.com', ('10.0.0.2', 5333)),
        (b'\x01bar.com', ('10.0.0.2', 5333)),
        (b'\x01foo.com', ('10.0.0.1', 3333)),
    ]

    s, o, e = sniffcli()
    assert o == '''Listening to 224.0.0.70:5333
10.0.0.2:5333 discoverfoo.com
10.0.0.2:5333 discoverbar.com
10.0.0.1:3333 discoverfoo.com
'''
    socketclass_mock.assert_called_once()
    sock = socketclass_mock.return_value
    sock.settimeout.assert_not_called()
