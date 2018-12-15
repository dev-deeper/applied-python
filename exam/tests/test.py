from io import StringIO
from unittest import TestCase, main, mock

import main as app


class TestUtil(TestCase):
    @mock.patch('sys.stdout', new_callable=StringIO)
    def main_handler(self, input_lines, mock_stdout):
        with mock.patch('builtins.input', side_effect=input_lines):
            app.main()
        return mock_stdout.getvalue()

    def test(self):
        user_input = [
            'log1 5',
            'log1 7',
            'log1 10',
            'log2 12',
            'log3 5',
            'log1 7',
            'log1 7',
            'log1 7',
            ''
        ]
        right_output = 'file 1 line 5\n' \
                       'file 1 line 7\n' \
                       'file 1 line 10\n' \
                       'file 2 line 12\n' \
                       'file 3 line 5\n' \
                       'file 1 line 7\n' \
                       'file 1 line 7\n' \
                       'file 1 line 7\n'
        self.assertEqual(self.main_handler(user_input), right_output)


if __name__ == '__main__':
    main()
