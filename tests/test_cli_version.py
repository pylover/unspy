from bddcli import Application, Given, status, stdout, given, when


def test_cli_version():
    from uns import __version__
    app = Application('foo', 'uns.cli:UNS.quickstart')

    with Given(app):
        assert status == 0
        assert stdout.startswith('usage: foo [-h] [-v]')

        when(given + '--version')
        assert status == 0
        assert stdout.startswith(__version__)

        when(given + '-v')
        assert status == 0
        assert stdout.startswith(__version__)
