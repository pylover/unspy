def test_cli_answer(socketclass_mock, answercli):
    sock = socketclass_mock.return_value
    s, o, e = answercli('h.foo')
    assert s == 0
    assert e == ''
    assert o == 'Answering h.foo to 224.0.0.70:5333\n'
    sock.sendto.assert_called_with(b'\x02h.foo', ('224.0.0.70', 5333))
