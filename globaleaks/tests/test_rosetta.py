from twisted.internet.defer import inlineCallbacks
from globaleaks.tests import helpers
from globaleaks.handlers import admin
import uuid

text_field =  {
        u'name': u'Localized name 1',
        u'hint': u"Localized hint 1",
        u'presentation_order': 0,
        u'key': unicode(uuid.uuid4()),
        u'required': True,
        u'preview': True,
        u'type': u'text',
        u'value': u''
}

class TestRosetta(helpers.TestHandler):
    _handler = admin.ContextInstance

    @inlineCallbacks
    def test_simple_update_fields(self):
        handler = self.request(role='admin')
        yield handler.get(self.dummyContext['context_gus'])

        self.assertTrue(isinstance(self.responses[0], dict))

        new_context_dict = dict(self.responses[0])
        new_context_dict['fields'] = [ text_field ]

        handler = self.request(new_context_dict, role='admin')
        yield handler.put(new_context_dict['context_gus'])

        self.assertEqual(self.responses[1]['fields'], [ text_field ] )

    # yep, need to be continued :(