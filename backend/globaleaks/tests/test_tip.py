# -*- encoding: utf-8 -*-
import re
from datetime import datetime

from twisted.internet.defer import inlineCallbacks

from globaleaks.settings import GLSetting, transact
from globaleaks.tests import helpers
from globaleaks.rest import errors, requests
from globaleaks.handlers import base, admin, submission, authentication, receiver, rtip, wbtip
from globaleaks.handlers.admin.field import create_field
from globaleaks.jobs import delivery_sched
from globaleaks import models
STATIC_PASSWORD = u'bungabunga ;( 12345'

class MockHandler(base.BaseHandler):

    def __init__(self):
        pass

class TTip(helpers.TestGL):

    # filled in setup
    context_desc = None
    receiver1_desc = receiver2_desc = None
    submission_desc = None

    # filled while the emulation tests
    receipt = None
    itip_id = wb_tip_id = rtip1_id = rtip2_id = None
    wb_data = receiver1_data = receiver2_data = None

    # These dummy variables follow
    # indeed in a different style
    # are used in the tip hollow
    # and is not a pattern defile

    dummySteps = [{
        'label': u'Presegnalazione',
        'description': u'',
        'hint': u'',
        'children': [u'd4f06ad1-eb7a-4b0d-984f-09373520cce7',
                     u'c4572574-6e6b-4d86-9a2a-ba2e9221467d',
                     u'6a6e9282-15e8-47cd-9cc6-35fd40a4a58f']
        },
        {
          'label': u'Segnalazione',
          'description': u'',
          'hint': u'',
          'children': []
        }
    ]

    tipContext = {
        'name': u'CtxName',
        'description': u'dummy context with default fields',
        'tip_max_access': 30,
        'tip_timetolive': 200,
        'file_max_download': 2,
        'receivers': [],
        'submission_timetolive': 100,
        'select_all_receivers': True,
        'receiver_introduction': u"¡⅜⅛⅝⅞⅝⅛⅛¡⅛⅛⅛",
        'postpone_superpower': False,
        'can_delete_submission': False,
        'maximum_selectable_receivers': 0,
        'show_small_cards': False,
        'show_receivers': True,
        'enable_private_messages': True,
        'presentation_order': 0,
        'steps': dummySteps
    }

    tipReceiver1 = {
        'mail_address': u'first@winstonsmith.org',
        'ping_mail_address': u'',
        'name': u'first',
        'description': u"I'm tha 1st",
        'can_delete_submission': True,
        'password': STATIC_PASSWORD,
        'file_notification': False,
        'comment_notification': True,
        'tip_notification': False,
        'message_notification': True,
        'ping_notification': False,
        'ping_mail_address': u'first@winstonsmith.org',
        'postpone_superpower': False,
        'gpg_key_status': u'Disabled',
        'gpg_key_info': None,
        'gpg_key_fingerprint': None,
        'gpg_key_remove': False,
        'gpg_key_armor': None,
        'gpg_key_expiration': u'',
        'presentation_order': 0,
        'timezone': 0,
        'language': u'en',
        'password_change_needed': True,
        'configuration': 'default'
    }

    tipReceiver2 = {
        'mail_address': u'second@winstonsmith.org',
        'ping_mail_address': u'',
        'name': u'second',
        'description': u"I'm tha 2nd",
        'can_delete_submission': False,
        'password': STATIC_PASSWORD,
        'file_notification': False,
        'message_notification': True,
        'postpone_superpower': True,
        'comment_notification': True,
        'tip_notification': False,
        'ping_notification': False,
        'ping_mail_address': u'second@winstonsmith.org',
        'gpg_key_status': u'Disabled',
        'gpg_key_info': None,
        'gpg_key_fingerprint': None,
        'gpg_key_remove': False,
        'gpg_key_armor': None,
        'gpg_key_expiration': u'',
        'presentation_order': 0,
        'timezone': 0,
        'language': u'en',
        'password_change_needed': True,
        'configuration': 'default'
    }

    tipOptions = {
        'global_delete': False,
    }

    commentCreation = {
        'content': '',
    }

class TestTipInstance(TTip):

    @inlineCallbacks
    def setup_tip_environment(self):

        basehandler = MockHandler()

        stuff = u'⅛⅛⅛£"$"$¼³²¼²³¼²³“““““ð'
        for attrname in models.Context.localized_strings:
            self.tipContext[attrname] = stuff

        basehandler.validate_jmessage(self.tipContext, requests.adminContextDesc)

        for idx, field in enumerate(self.dummyFields):
            f = yield create_field(field, 'en')
            self.dummyFields[idx]['id'] = f['id']

        self.tipContext['steps'][0]['children'] = [
            self.dummyFields[0], # Field 1
            self.dummyFields[1], # Field 2
            self.dummyFields[4]  # Generalities
        ]

        self.context_desc = yield admin.create_context(self.tipContext, 'en')

        self.tipReceiver1['contexts'] = self.tipReceiver2['contexts'] = [ self.context_desc['id'] ]

        for attrname in models.Receiver.localized_strings:
            self.tipReceiver1[attrname] = stuff
            self.tipReceiver2[attrname] = stuff

        basehandler.validate_jmessage( self.tipReceiver1, requests.adminReceiverDesc )
        basehandler.validate_jmessage( self.tipReceiver2, requests.adminReceiverDesc )

        self.receiver1_desc = yield admin.create_receiver(self.tipReceiver1, 'en')
        self.receiver2_desc = yield admin.create_receiver(self.tipReceiver2, 'en')

        self.assertEqual(self.receiver1_desc['contexts'], [ self.context_desc['id']])

        dummySubmissionDict = yield self.get_dummy_submission(self.context_desc['id'])
        basehandler.validate_jmessage(dummySubmissionDict, requests.wbSubmissionDesc)

        self.submission_desc = yield submission.create_submission(dummySubmissionDict, True, 'en')

        self.assertEqual(self.submission_desc['wb_steps'], dummySubmissionDict['wb_steps'])
        self.assertEqual(self.submission_desc['mark'], models.InternalTip._marker[1])
        # Ok, now the submission has been finalized, the tests can start.

    @inlineCallbacks
    def get_wb_receipt_on_finalized(self):
        """
        emulate auth, get wb_tip.id, get the data like GET /tip/xxx
        """
        if not self.receipt:
            self.receipt = yield submission.create_whistleblower_tip(self.submission_desc)

        self.assertGreater(len(self.receipt), 5)
        self.assertTrue(re.match(GLSetting.defaults.receipt_regexp, self.receipt) )

    @inlineCallbacks
    def wb_auth_with_receipt(self):

        if not self.wb_tip_id:
            self.get_wb_receipt_on_finalized()

            self.wb_tip_id = yield authentication.login_wb(self.receipt)
            # is the self.current_user.user_id

        self.assertTrue(re.match(requests.uuid_regexp, self.wb_tip_id))

    @inlineCallbacks
    def wb_auth_with_bad_receipt(self):

        fakereceipt = u"1234567890AA"

        retval = yield authentication.login_wb(fakereceipt)
        self.assertFalse(retval)

    @inlineCallbacks
    def wb_retrive_tip_data(self):
        self.wb_data = yield wbtip.get_tip(self.wb_tip_id, 'en')

        self.assertEqual(self.wb_data['wb_steps'], self.submission_desc['wb_steps'])

    @inlineCallbacks
    def create_receivers_tip(self):
        receiver_tips = yield delivery_sched.tip_creation()

        self.rtip1_id = receiver_tips[0]
        self.rtip2_id = receiver_tips[1]

        self.assertEqual(len(receiver_tips), 2)
        self.assertTrue(re.match(requests.uuid_regexp, receiver_tips[0]))
        self.assertTrue(re.match(requests.uuid_regexp, receiver_tips[1]))

    @inlineCallbacks
    def access_receivers_tip(self):
        auth1, _, _ = yield authentication.login_receiver(self.receiver1_desc['id'], STATIC_PASSWORD)
        self.assertEqual(auth1, self.receiver1_desc['id'])

        auth2, _, _ = yield authentication.login_receiver(self.receiver2_desc['id'], STATIC_PASSWORD)
        self.assertEqual(auth2, self.receiver2_desc['id'])

        tips_receiver_1 = yield receiver.get_receiver_tip_list(self.receiver1_desc['id'], 'en')
        tips_receiver_2 = yield receiver.get_receiver_tip_list(self.receiver2_desc['id'], 'en')

        for i in range(1, 2):
            self.receiver1_data = yield rtip.get_tip(auth1, tips_receiver_1[0]['id'], 'en')
            self.assertEqual(self.receiver1_data['wb_steps'], self.submission_desc['wb_steps'])
            self.assertEqual(self.receiver1_data['access_counter'], i)

        for i in range(1, 2):
            self.receiver2_data = yield rtip.get_tip(auth2, tips_receiver_2[0]['id'], 'en')
            self.assertEqual(self.receiver2_data['wb_steps'], self.submission_desc['wb_steps'])
            self.assertEqual(self.receiver2_data['access_counter'], i)

    @inlineCallbacks
    def strong_receiver_auth(self):
        """
        Test that an authenticated Receiver1 can't access to the Tip generated for Rcvr2
        """

        # Instead of yield authentication.login_receiver(username/pasword), is used:
        auth_receiver_1 = self.receiver1_desc['id']

        yield self.assertFailure(rtip.get_tip(auth_receiver_1, self.rtip2_id, 'en'),
                                 errors.TipIdNotFound)

    @inlineCallbacks
    def receiver1_get_tip_list(self):
        tiplist = yield receiver.get_receiver_tip_list(self.receiver1_desc['id'], 'en')

        # this test has been added to test issue/515
        self.assertTrue(isinstance(tiplist, list))
        self.assertTrue(isinstance(tiplist[0], dict))
        self.assertTrue(isinstance(tiplist[0]['preview'], list))
        # then the content here depends on the fields

    @inlineCallbacks
    def receiver_RW_comments(self):
        self.commentCreation['content'] = unicode("Comment N1 by R1")
        yield rtip.create_comment_receiver(
                                    self.receiver1_desc['id'],
                                    self.rtip1_id,
                                    self.commentCreation)

        cl = yield rtip.get_comment_list_receiver(
                                    self.receiver1_desc['id'],
                                    self.rtip1_id)
        self.assertEqual(len(cl), 1)

        self.commentCreation['content'] = unicode("Comment N2 by R2")
        yield rtip.create_comment_receiver(
                                    self.receiver2_desc['id'],
                                    self.rtip2_id,
                                    self.commentCreation)

        cl = yield rtip.get_comment_list_receiver(
                                    self.receiver2_desc['id'],
                                    self.rtip2_id)
        self.assertEqual(len(cl), 2)

    @inlineCallbacks
    def wb_RW_comments(self):
        self.commentCreation['content'] = unicode("I'm a WB comment")
        yield wbtip.create_comment_wb(self.wb_tip_id, self.commentCreation)

        cl = yield wbtip.get_comment_list_wb(self.wb_tip_id)
        self.assertEqual(len(cl), 3)

    @inlineCallbacks
    def wb_get_receiver_list(self, language):
        receiver_list = yield wbtip.get_receiver_list_wb(self.wb_tip_id, language)
        self.assertEqual(len(receiver_list), 2)
        self.assertEqual(receiver_list[0]['access_counter'] + receiver_list[1]['access_counter'], 2)

    @inlineCallbacks
    def receiver_get_receiver_list(self, language):
        receiver_list = yield rtip.get_receiver_list_receiver(self.receiver1_desc['id'], self.rtip1_id, language)
        self.assertEqual(len(receiver_list), 2)
        self.assertEqual(receiver_list[0]['access_counter'] + receiver_list[1]['access_counter'], 2)

        receiver_list = yield rtip.get_receiver_list_receiver(self.receiver2_desc['id'], self.rtip2_id, language)
        self.assertEqual(len(receiver_list), 2)
        self.assertEqual(receiver_list[0]['access_counter'] + receiver_list[1]['access_counter'], 2)

    @inlineCallbacks
    def fail_postpone_expiration_date(self):
        tip_expiring = yield rtip.get_tip(
            self.receiver1_desc['id'], self.rtip1_id, 'en')

        yield self.assertFailure(rtip.postpone_expiration_date(
                                     self.receiver1_desc['id'],
                                     self.rtip1_id),
                                 errors.ExtendTipLifeNotEnabled)

        tip_not_extended = yield rtip.get_tip(
            self.receiver1_desc['id'], self.rtip1_id, 'en')

        self.assertEqual(tip_expiring['expiration_date'], tip_not_extended['expiration_date'])

    @inlineCallbacks
    def verify_default_expiration_date(self):
        """
        that's the date status in this test (tip ttl 200 days)

        creation_date : 2013-10-31T21:22:14.481809
        potential_expiration_date : 2014-05-19 21:22:16.677997
        expiration_date : 2014-05-19T21:22:14.481711
        """
        context_list = yield admin.get_context_list('en')
        self.assertTrue(isinstance(context_list, list))
        self.assertEqual(len(context_list), 1)
        tip_ttl = context_list[0]['tip_timetolive']

        tip_expiring = yield rtip.get_tip(
            self.receiver1_desc['id'], self.rtip1_id, 'en')

        # TODO implement a more complete test

    @inlineCallbacks
    def update_node_properties(self):
        node_desc = yield admin.admin_serialize_node('en')
        self.assertEqual(node_desc['postpone_superpower'], False)
        node_desc['postpone_superpower'] = True

        stuff = u"³²¼½¬¼³²"
        for attrname in models.Node.localized_strings:
            node_desc[attrname] = stuff

        node_desc = yield admin.update_node(node_desc, True, 'en')
        self.assertEqual(node_desc['postpone_superpower'], True)

    @inlineCallbacks
    def success_postpone_expiration_date(self):
        """
        Tests with receiver1 and update with receiver2 is equal
        to use the the same receiver
        """
        tip_expiring = yield rtip.get_tip(
            self.receiver1_desc['id'], self.rtip1_id, 'en')

        yield rtip.postpone_expiration_date(
                    self.receiver2_desc['id'],
                    self.rtip2_id)

        tip_extended = yield rtip.get_tip(
            self.receiver1_desc['id'], self.rtip1_id, 'en')

        self.assertNotEqual(tip_expiring['expiration_date'], tip_extended['expiration_date'])

    @inlineCallbacks
    def postpone_comment_content_check(self):
        """
           'type': "1", # the first kind of structured system_comments
           'receiver_name': rtip.receiver.name,
           'now' : datetime_now(),
           'expire_on' : datetime_to_ISO8601(rtip.internaltip.expiration_date)
        """
        cl = yield rtip.get_comment_list_receiver(self.receiver1_desc['id'],
                                                 self.rtip1_id)

        self.assertEqual(cl[3]['type'], models.Comment._types[2]) # System (date extension)

        sys_comm = cl[3]

        self.assertEqual(sys_comm['system_content']['receiver_name'], self.receiver2_desc['name'])
        self.assertEqual(sys_comm['system_content']['type'], u"1")
        new_expire = sys_comm['system_content']['expire_on']

        # TODO implement a more complete test


    @inlineCallbacks
    def receiver2_fail_in_delete_internal_tip(self):
        yield self.assertFailure(rtip.delete_internal_tip(self.receiver2_desc['id'],
                                                          self.rtip2_id),
                                 errors.ForbiddenOperation)

    @inlineCallbacks
    def receiver2_personal_delete(self):
        yield rtip.delete_receiver_tip(self.receiver2_desc['id'], self.rtip2_id)


    @inlineCallbacks
    def receiver1_see_system_comments(self):
        cl = yield rtip.get_comment_list_receiver(self.receiver1_desc['id'],
                                        self.rtip1_id)

        self.assertEqual(len(cl), 5)
        self.assertEqual(cl[0]['type'], models.Comment._types[0]) # Receiver (Rcvr1)
        self.assertEqual(cl[1]['type'], models.Comment._types[0]) # Receiver (Rcvr2)
        self.assertEqual(cl[2]['type'], models.Comment._types[1]) # Wb

        self.assertEqual(cl[3]['type'], models.Comment._types[2]) # System (date extension)
        self.assertEqual(cl[3]['system_content']['receiver_name'], self.receiver2_desc['name'])

        self.assertEqual(cl[4]['type'], models.Comment._types[2]) # System


    @inlineCallbacks
    def receiver1_global_delete_tip(self):

        yield rtip.delete_internal_tip(self.receiver1_desc['id'],
            self.rtip1_id)

        self.assertFailure(rtip.get_tip(self.receiver1_desc['id'], self.rtip1_id, 'en'),
                           errors.TipIdNotFound)

    @inlineCallbacks
    def check_wb_messages_expected(self, expected_msgs):

        x = yield wbtip.get_messages_content(self.wb_tip_id, self.receiver1_desc['id'])
        self.assertEqual(len(x), expected_msgs)

        y = yield wbtip.get_messages_content(self.wb_tip_id, self.receiver2_desc['id'])
        self.assertEqual(len(y), expected_msgs)

    @inlineCallbacks
    def check_receiver_messages_expected(self, expected_msgs):

        x = yield rtip.get_messages_list(self.receiver1_desc['id'], self.rtip1_id)
        self.assertEqual(len(x), expected_msgs)

        y = yield rtip.get_messages_list(self.receiver2_desc['id'], self.rtip2_id)
        self.assertEqual(len(y), expected_msgs)

        # receiver 1 and tip 2 access test
        yield self.assertFailure(rtip.get_messages_list(self.receiver1_desc['id'], self.rtip2_id),
                                 errors.TipIdNotFound)

    @inlineCallbacks
    def do_wb_messages(self):

        before = yield wbtip.get_receiver_list_wb(self.wb_tip_id, 'en')


        # the direct message has been sent to the receiver 1, and receiver 1
        # is on the element [0] of the list.
        self.assertEqual(len(before), 2)
        self.assertEqual(before[0]['your_messages'], 0)

        msgrequest = { 'content': u'a msg from wb to receiver1' }
        x = yield wbtip.create_message_wb(self.wb_tip_id,
                                          self.receiver1_desc['id'], msgrequest)

        self.assertEqual(x['author'], u'Whistleblower')

        after = yield wbtip.get_receiver_list_wb(self.wb_tip_id, 'en')

        for receivers_message in after:
            if receivers_message['id'] == self.receiver1_desc['id']:
                self.assertEqual(receivers_message['your_messages'], 1)
            else:
                self.assertEqual(receivers_message['your_messages'], 0)

        # and now, two messages for the second receiver
        msgrequest = { 'content': u'#1/2 msg from wb to receiver2' }
        yield wbtip.create_message_wb(self.wb_tip_id,
                                          self.receiver2_desc['id'], msgrequest)
        msgrequest = { 'content': u'#2/2 msg from wb to receiver2' }
        yield wbtip.create_message_wb(self.wb_tip_id,
                                          self.receiver2_desc['id'], msgrequest)

        end = yield wbtip.get_receiver_list_wb(self.wb_tip_id, 'en')

        for receivers_message in end:
            if receivers_message['id'] == self.receiver2_desc['id']:
                self.assertEqual(receivers_message['your_messages'], 2)
            else: # the messages from Receiver1 are not changed, right ?
                self.assertEqual(receivers_message['your_messages'], 1)

    @inlineCallbacks
    def do_receivers_messages_and_unread_verification(self):

        # Receiver1 check the presence of the whistleblower message (only 1)
        x = yield receiver.get_receiver_tip_list(self.receiver1_desc['id'], 'en')
        self.assertEqual(x[0]['unread_messages'], 1)

        # Receiver1 send one message
        msgrequest = { 'content': u'Receiver1 send a message to WB' }
        k = yield rtip.create_message_receiver(self.receiver1_desc['id'],
                                               self.rtip1_id, msgrequest)
        self.assertEqual(k['visualized'], False)
        self.assertEqual(k['content'], msgrequest['content'])

        # Whistleblower check the presence of receiver1 unread message
        receiver_info_list = yield wbtip.get_receiver_list_wb(self.wb_tip_id, 'en')

        for r in receiver_info_list:
            if r['id'] == self.receiver1_desc['id']:
                self.assertEqual(r['name'], self.receiver1_desc['name'])
                self.assertEqual(r['unread_messages'], 1)
                self.assertEqual(r['your_messages'], 1)
            else:
                self.assertEqual(r['name'], self.receiver2_desc['name'])
                self.assertEqual(r['unread_messages'], 0)
                self.assertEqual(r['your_messages'], 2)

        # Receiver2 check the presence of the whistleblower message (2 expected)
        a = yield receiver.get_receiver_tip_list(self.receiver1_desc['id'], 'en')
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0]['your_messages'], 1)
        self.assertEqual(a[0]['unread_messages'], 1)
        self.assertEqual(a[0]['read_messages'], 0)

        # Receiver2 READ the messages from the whistleblower
        unread = yield rtip.get_messages_list(self.receiver2_desc['id'], self.rtip2_id)
        self.assertEqual(unread[0]['visualized'], unread[1]['visualized'])
        self.assertEqual(unread[0]['visualized'], False)

        readed = yield rtip.get_messages_list(self.receiver2_desc['id'], self.rtip2_id)
        self.assertEqual(readed[0]['visualized'], readed[1]['visualized'])
        self.assertEqual(readed[0]['visualized'], True)

        # Receiver2 send two message
        msgrequest = { 'content': u'Receiver2 send #1/2 message to WB' }
        a1 = yield rtip.create_message_receiver(self.receiver2_desc['id'],
                                                self.rtip2_id, msgrequest)
        msgrequest = { 'content': u'Receiver2 send #2/2 message to WB' }
        a2 = yield rtip.create_message_receiver(self.receiver2_desc['id'],
                                                self.rtip2_id, msgrequest)

        # Whistleblower read the messages from Receiver2
        wunread = yield wbtip.get_messages_content(self.wb_tip_id, self.receiver2_desc['id'])
        self.assertEqual(len(wunread), 4) # two msg from Wb, two from R2
        self.assertFalse(wunread[2]['visualized'])
        self.assertFalse(wunread[3]['visualized'])

        wreaded = yield wbtip.get_messages_content(self.wb_tip_id, self.receiver2_desc['id'])
        self.assertTrue(wreaded[2]['visualized'])
        self.assertTrue(wreaded[3]['visualized'])

        # Whistleblower check 0 unread messages from Receiver2, and still 1 from R1
        end = yield wbtip.get_receiver_list_wb(self.wb_tip_id, 'en')
        

        for recv in end:
            if recv['id'] == self.receiver2_desc['id']:
                self.assertEqual(recv['unread_messages'], 0)
            else:
                self.assertEqual(recv['unread_messages'], 1)

    @inlineCallbacks
    def test_full_receiver_wb_workflow(self):
        yield self.setup_tip_environment()
        yield self.get_wb_receipt_on_finalized()
        yield self.wb_auth_with_receipt()
        yield self.wb_auth_with_bad_receipt()
        yield self.wb_retrive_tip_data()
        yield self.create_receivers_tip()
        yield self.access_receivers_tip()
        yield self.strong_receiver_auth()

        # test of direct messages
        yield self.check_wb_messages_expected(0)
        yield self.check_receiver_messages_expected(0)
        yield self.do_wb_messages()
        yield self.do_receivers_messages_and_unread_verification()
        # end direct messages block

        # this is the only test on receiver handler and not in tip handler:
        yield self.receiver1_get_tip_list()
        yield self.receiver_RW_comments()
        yield self.wb_RW_comments()
        yield self.wb_get_receiver_list(GLSetting.memory_copy.default_language)
        yield self.receiver_get_receiver_list(GLSetting.memory_copy.default_language)
        # test expiration date
        yield self.fail_postpone_expiration_date()
        yield self.verify_default_expiration_date()
        yield self.update_node_properties()
        yield self.success_postpone_expiration_date()
        yield self.postpone_comment_content_check()
        # end of test
        yield self.receiver2_fail_in_delete_internal_tip()
        yield self.receiver2_personal_delete()
        yield self.receiver1_see_system_comments()
        yield self.receiver1_global_delete_tip()
