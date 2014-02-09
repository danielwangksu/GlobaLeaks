# -*- encoding: utf-8 -*-

from twisted.internet.defer import inlineCallbacks

from globaleaks.tests import helpers
from globaleaks.models import Stats
from globaleaks.handlers import node, submission, files
from globaleaks.jobs import statistics_sched
from globaleaks.settings import transact, GLSetting, external_counted_events

class TestEmail(helpers.TestGL):

    def increment_accesses(self, amount):

        for element in external_counted_events.keys():
            GLSetting.anomalies_counter[element] = amount

    @inlineCallbacks
    def test_anomalies(self):

        yield helpers.TestGL.setUp(self)

        print "First round 10"
        self.increment_accesses(10)
        statistics_sched.APSAnomalies().operation()

        print "Second round 30"
        self.increment_accesses(30)
        statistics_sched.APSAnomalies().operation()

        print "Third round 30"
        self.increment_accesses(30)
        statistics_sched.APSAnomalies().operation()

        print "Stats!"
        yield statistics_sched.APSStatistics().operation()


