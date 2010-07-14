# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import nagiosplugin.check
import nagiosplugin.state
import nagiosplugin.test
import unittest
from nagiosplugin import controller


class MockCheck(nagiosplugin.check.Check):

    def __init__(self, optparser, logger):
        (self.op, self.log) = (optparser, logger)

    def obtain_data(self, opts, args):
        self.data = 4


class StatePerformanceCheck(MockCheck):

    def states(self):
        return [nagiosplugin.state.Warning([u'yellow', u'long1', u'long2'])]

    def performances(self):
        return [u'perf=4']

class DebugLogCheck(MockCheck):

    def obtain_data(self, *args):
        self.log.debug(u'debug')
        self.log.info(u'info')
        self.log.warning(u'warning')


class ControllerTest(unittest.TestCase):

    def test_init_creates_check_object(self):
        c = controller.Controller(MockCheck)
        self.assert_(isinstance(c.check, MockCheck),
                     u'%r is not an instance of MockCheck' % c.check)

    def test_dormant_check_results_is_unknown(self):
        c = controller.Controller(MockCheck)
        self.assert_(isinstance(c.dominant_state, nagiosplugin.state.Unknown))

    def test_exception_results_in_unknown(self):
        class FailingCheck(MockCheck):
            def obtain_data(self, *args):
                raise RuntimeError(u'unhandled error')
        c = controller.Controller(FailingCheck)
        self.assertEqual(u'CHECK UNKNOWN - unhandled error\n', c.format())

    def test_format_with_default_message(self):
        class DefaultMessageCheck(MockCheck):
            @property
            def default_message(self):
                return u'default message'
        c = controller.Controller(DefaultMessageCheck)
        self.assertEqual(u'CHECK OK - default message\n', c.format())

    def test_controller_should_call_obtain_data(self):
        c = controller.Controller(MockCheck)
        self.assertEqual(c.check.data, 4)

    def test_controller_should_call_states_and_performances(self):
        c = controller.Controller(StatePerformanceCheck)
        self.assert_(isinstance(c.states[0], nagiosplugin.state.Warning))
        self.assertEqual(u'perf=4', c.performances[0])

    def test_format(self):
        c = controller.Controller(StatePerformanceCheck)
        self.assertEqual(u'CHECK WARNING - yellow | perf=4\nlong1\nlong2\n',
                         c.format())

    def test_sigalarm_should_raise_TimeoutError(self):
        c = controller.Controller(MockCheck)
        self.assertRaises(controller.TimeoutError,
                          c.timeout_handler, None, None)

    def test_process_timeouterror(self):
        class TimeoutCheck(MockCheck):
            def obtain_data(self, *args):
                raise controller.TimeoutError()
        c = controller.Controller(TimeoutCheck)
        self.assertEqual(u'CHECK UNKNOWN - timeout of 15s exceeded\n',
                         c.format())

    def test_logger_init(self):
        c = controller.Controller(MockCheck)
        self.assert_(isinstance(c.check.log, logging.Logger),
                     u'%r is not a Logger instance' % c.check.log)

    def test_logger_debug(self):
        c = controller.Controller(DebugLogCheck, ['-vvv'])
        self.assertEqual(u'debug\ninfo\nwarning\n', c.logstream.getvalue())

    def test_logger_warning(self):
        c = controller.Controller(DebugLogCheck, ['-v'])
        self.assertEqual(u'warning\n', c.logstream.getvalue())


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ControllerTest)
    return suite

if __name__ == '__main__':
    unittest.main()
