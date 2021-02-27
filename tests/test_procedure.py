import os
import tempfile
import time
import unittest

from platypush.message.event.custom import CustomEvent
from . import BaseHttpTest, conf_dir


@unittest.skip('Skipped until I can find a way to properly clean up the environment from the previous tests and start '
               'a new platform')
class TestProcedure(BaseHttpTest):
    """
    Test the execution of configured procedures.
    """

    config_file = os.path.join(conf_dir, 'test_procedure_config.yaml')

    def setUp(self) -> None:
        super().setUp()
        self.register_user()
        self.tmp_file = tempfile.NamedTemporaryFile(prefix='platypush-test-procedure-', suffix='.txt', delete=False)

    def tearDown(self):
        if os.path.isfile(self.tmp_file.name):
            os.unlink(self.tmp_file.name)
        super().tearDown()

    def check_file_content(self, expected_content: str):
        self.assertTrue(os.path.isfile(self.tmp_file.name), 'The expected output file was not created')
        with open(self.tmp_file.name, 'r') as f:
            content = f.read()

        self.assertEqual(content, expected_content, 'The output file did not contain the expected text',
                         expected=expected_content, actual=content)

    def test_procedure_call(self):
        output_text = 'Procedure test'
        self.send_request(
            action='procedure.write_file',
            args={
                'file': self.tmp_file.name,
                'content': output_text,
            })

        self.check_file_content(expected_content=output_text)

    def test_procedure_from_event(self):
        output_text = 'Procedure from event test'
        event_type = 'platypush_test_procedure_from_event'
        self.app.bus.post(CustomEvent(subtype=event_type, file=self.tmp_file.name, content=output_text))
        time.sleep(3)
        self.check_file_content(output_text)


if __name__ == '__main__':
    unittest.main()


# vim:sw=4:ts=4:et:
