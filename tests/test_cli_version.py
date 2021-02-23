def test_cli_version(cliapp):
    from uns import __version__

    s, o, e = cliapp()
    assert e == ''
    assert s == 0
    assert o.startswith('usage: uns [-h] [-v]')

    s, o, e = cliapp('--version')
    assert s == 0
    assert o.startswith(__version__)

    s, o, e = cliapp('-v')
    assert s == 0
    assert o.startswith(__version__)
