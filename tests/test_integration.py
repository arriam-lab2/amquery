import os
import unittest
from amquery import cli
from click.testing import CliRunner


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.index_name = 'test'

    def test_init(self):
        runner = CliRunner()
        result = runner.invoke(cli.amq_cli, ["init", self.index_name])
        assert(result.exit_code == 0)

    def _get_test_files(self):
        test_data_dir = os.path.dirname(os.path.abspath(__file__)) + "/test_data"
        return [os.path.join(test_data_dir, f) for f in os.listdir(test_data_dir)]

    def test_build(self):
        runner = CliRunner()
        result = runner.invoke(cli.amq_cli, ["build", *self._get_test_files()])
        assert(result.exit_code == 0)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
