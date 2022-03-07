"""
test class TagString
"""

import unittest

import lib


class TestTagString(unittest.TestCase):
    """
    test class
    """

    def test_i_check_tags(self):
        """
        test procedure
        """

        with self.assertRaises(AssertionError) as context:
            o_ts = lib.TagString("", "-")
        self.assertIn(
            's_tag_prefix must not be a character which can be used '
            'in a tag itself', str(context.exception))

        with self.assertRaises(AssertionError) as context:
            o_ts = lib.TagString("", "12")
        self.assertIn(
            's_tag_prefix must be a single character',
            str(context.exception))

        o_ts = lib.TagString("#tag, #tag, #othertag")
        self.assertEqual(o_ts.i_check_tags(0), 2)

    def test_init_no_tags(self):
        """
        test procedure
        """
        o_ts = lib.TagString("string with no tags")
        self.assertEqual(o_ts.i_check_tags(0), 0)
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.s_get_tag_prefix(), '#')

    def test_init_with_several_tags(self):
        """
        test procedures
        """
        o_ts = lib.TagString("#tag und #tags und noch ein #tag")
        self.assertFalse(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), ["#tag"])

    def test_init_simple_tags(self):
        """
        test procedure
        """
        o_ts = lib.TagString("string with 1 #tag")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(1), 0)
        o_ts.with_simple('#tag')
        self.assertEqual(o_ts.i_check_tags(1), 0)

        o_ts = lib.TagString("string with 2 #tag #tags")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(2), 0)
        o_ts.with_simple('#tag')
        self.assertEqual(o_ts.i_check_tags(2), 0)
        self.assertTrue(o_ts.b_has_simple_tag('#tag'))

        o_ts = lib.TagString("string with 2 #tags")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(1), 0)
        o_ts.with_simple('#tag')
        self.assertEqual(o_ts.i_check_tags(1), 0)
        self.assertFalse(o_ts.b_has_simple_tag('#tag'))

    def test_excls_tags(self):
        """
        test procedures
        """
        o_ts = lib.TagString("string with no tags")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(0), 0)

        o_ts.with_excls('#media', ['#video', '#audio'])
        self.assertIsNone(o_ts.s_get_excls_tag('#media'))
        self.assertEqual(o_ts.s_get_excls_tag('#media', '#other'), '#other')

        o_ts = lib.TagString("string with #video tag")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(1), 0)

        o_ts.with_excls('#media', ['#video', '#audio'])
        self.assertEqual(o_ts.i_check_tags(1), 0)
        self.assertTrue(o_ts.b_has_excls_tag('#media', '#video'))
        self.assertFalse(o_ts.b_has_excls_tag('#media', '#audio'))
        self.assertFalse(o_ts.b_has_excls_tag('#media', '#other'))
        self.assertEqual(o_ts.s_get_excls_tag('#media'), '#video')

        o_ts = lib.TagString("string with #audio tag")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(1), 0)

        o_ts.with_excls('#media', ['#video', '#audio'])
        self.assertEqual(o_ts.s_get_excls_tag('#media'), '#audio')

        o_ts = lib.TagString("string with #video and #audio tag")
        self.assertTrue(o_ts.b_has_unique_tags())
        self.assertEqual(o_ts.l_duplicate_tags(), [])
        self.assertEqual(o_ts.i_check_tags(2), 0)

        o_ts.with_excls('#media', ['#video', '#audio'])
        self.assertEqual(o_ts.i_check_tags(2), 1)

    def test_date_tags(self):
        """
        test procedures
        """
        o_ts = lib.TagString(
            "string with date tags #2021-10-04, #2021-09-31")
        self.assertEqual(o_ts.i_check_tags(2), 0)
        o_ts.with_dates()
        self.assertEqual(o_ts.i_check_tags(2), 3)

    def test_all_tag_types(self):
        """
        test procedure
        """
        o_ts = lib.TagString(
            'this string contains all types of tags:}\n' +
            '#tag1, #subtag1, #2021-10-01, #2021-10-02')
        self.assertEqual(o_ts.i_check_tags(4), 0)
        self.assertEqual(
            o_ts.l_unknown_tags(),
            ['#tag1', '#subtag1', '#2021-10-01', '#2021-10-02']
            )
        o_ts.with_simple('#tag1')
        self.assertEqual(
            o_ts.l_unknown_tags(),
            ['#subtag1', '#2021-10-01', '#2021-10-02']
            )
        o_ts.with_simple('#tag2')
        self.assertEqual(
            o_ts.l_unknown_tags(),
            ['#subtag1', '#2021-10-01', '#2021-10-02']
            )
        self.assertEqual(o_ts.i_check_tags(4), 0)
        o_ts.with_excls('#subtag', ['#subtag1', '#subtag2'])
        self.assertEqual(o_ts.i_check_tags(4), 0)
        self.assertEqual(
            o_ts.l_unknown_tags(),
            ['#2021-10-01', '#2021-10-02']
            )
        self.assertEqual(o_ts.s_get_excls_tag('#subtag'), '#subtag1')
        o_ts.with_dates()
        self.assertEqual(o_ts.l_unknown_tags(), [])
        self.assertEqual(o_ts.i_check_tags(4), 0)
        self.assertTrue(o_ts.b_has_date_tag('2021-10-01'))
        self.assertTrue(o_ts.b_has_date_tag('2021-10-02'))
        self.assertFalse(o_ts.b_has_date_tag('2021-10-03'))
        self.assertFalse(o_ts.b_has_date_tag('#tag1'))
        self.assertFalse(o_ts.b_has_date_tag('#subtag'))
        o_ts.dump()


if __name__ == '__main__':
    unittest.main()
