def test_cli_resolve(socketclass_mock, cliapp):
    status, stdout, stderr = cliapp('resolve', 'foo.com')
    assert stderr == ''
    assert status == 0
    assert stdout == '10.0.0.2 foo.com\n'
    socketclass_mock.assert_called_once()


if __name__ == '__main__':
    from uns.cli import UNS
    UNS.quickstart(['resolve', 'foo.com'])
