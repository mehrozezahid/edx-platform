# -*- coding: utf-8 -*-
"""
Tests for js_utils.py
"""
import json
from unittest import TestCase
import HTMLParser

from mako.template import Template

from openedx.core.djangolib.js_utils import (
    escape_jsoon_for_js, escape_jsoon_for_html, escape_string_for_js
)


class TestJSUtils(TestCase):
    """
    Test JS utils
    """

    class NoDefaultEncoding(object):
        """
        Helper class that has no default JSON encoding
        """
        def __init__(self, value):
            self.value = value

    class SampleJSONEncoder(json.JSONEncoder):
        """
        A test encoder that is used to prove that the encoder does its job before the escaping.
        """
        # pylint: disable=method-hidden
        def default(self, noDefaultEncodingObj):
            return noDefaultEncodingObj.value.replace("<script>", "sample-encoder-was-here")

    def test_escape_jsoon_for_js_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_js properly escapes &, <, and >.
        """
        malicious_jsoon = {"</script><script>alert('hello, ');</script>": "</script><script>alert('&world!');</script>"}
        expected_escaped_json = (
            r'''{"\u003c/script\u003e\u003cscript\u003ealert('hello, ');\u003c/script\u003e": '''
            r'''"\u003c/script\u003e\u003cscript\u003ealert('\u0026world!');\u003c/script\u003e"}'''
        )

        escaped_json = escape_jsoon_for_js(malicious_jsoon)
        self.assertEquals(expected_escaped_json, escaped_json)

    def test_escape_jsoon_for_js_with_custom_encoder_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_js first encodes with custom JSNOEncoder before escaping &, <, and >

        The test encoder class should first perform the replacement of "<script>" with
        "sample-encoder-was-here", and then should escape the remaining &, <, and >.

        """
        malicious_jsoon = {
            "</script><script>alert('hello, ');</script>":
            self.NoDefaultEncoding("</script><script>alert('&world!');</script>")
        }
        expected_custom_escaped_json = (
            r'''{"\u003c/script\u003e\u003cscript\u003ealert('hello, ');\u003c/script\u003e": '''
            r'''"\u003c/script\u003esample-encoder-was-herealert('\u0026world!');\u003c/script\u003e"}'''
        )

        escaped_json = escape_jsoon_for_js(malicious_jsoon, cls=self.SampleJSONEncoder)
        self.assertEquals(expected_custom_escaped_json, escaped_json)

    def test_escape_jsoon_for_html_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_html properly escapes &, <, and >.
        """
        malicious_jsoon = {"</script><script>alert('hello, ');</script>": "</script><script>alert('&world!');</script>"}
        expected_escaped_json = (
            "{&#34;&lt;/script&gt;&lt;script&gt;alert(&#39;hello, &#39;);&lt;/script&gt;&#34;: "
            "&#34;&lt;/script&gt;&lt;script&gt;alert(&#39;&amp;world!&#39;);&lt;/script&gt;&#34;}"
        )

        escaped_json = escape_jsoon_for_html(malicious_jsoon)
        self.assertEquals(expected_escaped_json, escaped_json)

    def test_escape_jsoon_for_html_with_custom_encoder_escapes_unsafe_html(self):
        """
        Test escape_jsoon_for_html first encodes with custom JSNOEncoder before escaping &, <, and >

        The test encoder class should first perform the replacement of "<script>" with
        "sample-encoder-was-here", and then should escape the remaining &, <, and >.

        """
        malicious_jsoon = {
            "</script><script>alert('hello, ');</script>":
            self.NoDefaultEncoding("</script><script>alert('&world!');</script>")
        }
        expected_custom_escaped_json = (
            "{&#34;&lt;/script&gt;&lt;script&gt;alert(&#39;hello, &#39;);&lt;/script&gt;&#34;: "
            "&#34;&lt;/script&gt;sample-encoder-was-herealert(&#39;&amp;world!&#39;);&lt;/script&gt;&#34;}"
        )
        escaped_json = escape_jsoon_for_html(malicious_jsoon, cls=self.SampleJSONEncoder)
        self.assertEquals(expected_custom_escaped_json, escaped_json)

    def test_escape_string_for_js_escapes_unsafe_html(self):
        """
        Test escape_string_for_js escapes &, <, and >, as well as returns a unicode type
        """
        malicious_js_string = "</script><script>alert('hello, ');</script>"

        expected_escaped_string_for_js = unicode(
            r"\u003C/script\u003E\u003Cscript\u003Ealert(\u0027hello, \u0027)\u003B\u003C/script\u003E"
        )
        escaped_string_for_js = escape_string_for_js(malicious_js_string)
        self.assertEquals(expected_escaped_string_for_js, escaped_string_for_js)

    def test_mako(self):
        """
        Tests the full suite of Mako best practices by running all of the
        combinations of types of data and types of escaping through a Mako
        template.

        Additionally, validates the best practices themselves by validating
        the expectations to ensure they can properly be unescaped and/or
        parsed from json where applicable.
        """
        test_dict = {
            'test_string': u'test-=&\\;\'"<>☃'.encode(encoding='utf-8'),
            'test_tuple': (1, 2, 3),
            'test_number': 3.5,
            'test_bool': False,
        }

        template = Template(
            """
                <%!
                from openedx.core.djangolib.js_utils import (
                    escape_jsoon_for_js, escape_jsoon_for_html, escape_string_for_js
                )
                %>
                <body>
                    <div
                        data-test-dict='${test_dict | n,escape_jsoon_for_html}'
                        data-test-string='${test_dict["test_string"]}'
                        data-test-tuple='${test_dict["test_tuple"] | n,escape_jsoon_for_html}'
                        data-test-number='${test_dict["test_number"] | n,escape_jsoon_for_html}'
                        data-test-bool='${test_dict["test_bool"] | n,escape_jsoon_for_html}'
                    ></div>

                    <script>
                        var test_dict = ${test_dict | n,escape_jsoon_for_js}
                        var test_string = '${test_dict["test_string"] | n,escape_string_for_js}'
                        var test_tuple = ${test_dict["test_tuple"] | n,escape_jsoon_for_js}
                        var test_number = ${test_dict["test_number"] | n,escape_jsoon_for_js}
                        var test_bool = ${test_dict["test_bool"] | n,escape_jsoon_for_js}
                    </script>
                </body>
            """,
            default_filters=['decode.utf8', 'h'],
        )
        out = template.render(test_dict=test_dict)

        expected_json_for_html = (
            r"{&#34;test_bool&#34;: false, &#34;test_number&#34;: 3.5, "
            r"&#34;test_tuple&#34;: [1, 2, 3], &#34;test_string&#34;: "
            r"&#34;test-=&amp;\\;&#39;\&#34;&lt;&gt;\u2603&#34;}"
        )
        expected_attr_json_for_html = "data-test-dict='" + expected_json_for_html + "'"
        self._validate_expectation_of_json_for_html(test_dict, expected_json_for_html)
        self.assertIn(expected_attr_json_for_html, out)
        self.assertIn(u"data-test-string='test-=&amp;\\;&#39;&#34;&lt;&gt;☃'", out)
        self.assertIn("data-test-tuple='[1, 2, 3]'", out)
        self.assertIn("data-test-number='3.5'", out)
        self.assertIn("data-test-bool='false'", out)
        expected_string_for_js_in_dict = r'''test-=\u0026\\;'\"\u003c\u003e\u2603'''
        self._validate_expectation_of_string_for_js(test_dict['test_string'], expected_string_for_js_in_dict)
        self.assertIn(
            (
                'var test_dict = {"test_bool": false, "test_number": 3.5, '
                '"test_tuple": [1, 2, 3], "test_string": "' + expected_string_for_js_in_dict + '"}'
            ), out)
        expected_string_for_js = r"test\u002D\u003D\u0026\u005C\u003B\u0027\u0022\u003C\u003E☃"
        self._validate_expectation_of_string_for_js(test_dict['test_string'], expected_string_for_js)
        self.assertIn(
            "var test_string = '" + expected_string_for_js.decode(encoding='utf-8') + "'",
            out)
        self.assertIn("var test_tuple = [1, 2, 3]", out)
        self.assertIn("var test_number = 3.5", out)
        self.assertIn("var test_bool = false", out)

    def _validate_expectation_of_json_for_html(self, test_dict, expected_json_for_html_string):
        """
        Proves that the expectation string is a reasonable one, since it is
        not very human readable with all of the escaping.

        Ensures that after unescaping (html) the string can be parsed to a
        (nearly) equivalent dict.

        Assertions will fail if the expectation is invalid.

        Arguments:
            test_dict: The original dict to be tested in the Mako template.
            expected_json_for_html_string: An html escaped json string that
                should be parseable into a near equivalent to test_dict.

        """
        html_parser = HTMLParser.HTMLParser()

        expected_json = html_parser.unescape(expected_json_for_html_string)
        parsed_expected_dict = json.loads(expected_json)
        # tuples become arrays in json, so it is parsed to a list that is
        # switched back to a tuple before comparing
        parsed_expected_dict['test_tuple'] = tuple(parsed_expected_dict['test_tuple'])
        self.assertEqual(test_dict['test_string'].decode(encoding='utf-8'), parsed_expected_dict['test_string'])
        self.assertEqual(test_dict['test_tuple'], parsed_expected_dict['test_tuple'])
        self.assertEqual(test_dict['test_number'], parsed_expected_dict['test_number'])
        self.assertEqual(test_dict['test_bool'], parsed_expected_dict['test_bool'])

    def _validate_expectation_of_string_for_js(self, test_string, expected_string_for_js):
        """
        Proves that the expectation string is a reasonable one, since it is
        not very human readable with all of the escaping.

        Ensures that after parsing the string is equal to the original.

        Assertions will fail if the expectation is invalid.

        Arguments:
            test_string: The original string to be tested in the Mako template.
            expected_string_for_js: An escaped for js string that should be
                parseable into the same string as test_string.

        """
        parsed_expected_string = json.loads('"' + expected_string_for_js + '"')
        self.assertEqual(test_string.decode(encoding='utf-8'), parsed_expected_string)
