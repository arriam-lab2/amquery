import os
import unittest
from amquery import cli
from click.testing import CliRunner


class TestIntegration(unittest.TestCase):
    def test_init(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["init"])
        assert(result.exit_code == 0)

    def _get_test_files(self):
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")
        return [os.path.join(test_data_dir, "all.fasta")]

    def test_build(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["build", *self._get_test_files()])
        assert(result.exit_code == 0)

    def test_stats(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["stats"])
        assert(result.exit_code == 0)

    def test_find(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["find", "115", "-k", "5"])
        assert(result.exit_code == 0)


if __name__ == '__main__':
    unittest.main()
