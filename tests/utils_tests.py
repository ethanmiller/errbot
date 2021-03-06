# coding=utf-8
import logging
from datetime import timedelta
import unittest
from tempfile import mkdtemp
from nose.tools import raises

from errbot.errBot import bot_config_defaults
from errbot.main import CORE_STORAGE
from errbot.specific_plugin_manager import SpecificPluginManager
from errbot.storage.base import StoragePluginBase
from errbot.utils import *
from errbot.storage import StoreMixin

log = logging.getLogger(__name__)


def vc(v1, v2):
    return version2array(v1) < version2array(v2)


def test_version_check():
    yield vc, '2.0.0', '2.0.1'
    yield vc, '2.0.0', '2.1.0'
    yield vc, '2.0.0', '3.0.0'
    yield vc, '2.0.0-alpha', '2.0.0-beta'
    yield vc, '2.0.0-beta', '2.0.0-rc1'
    yield vc, '2.0.0-rc1', '2.0.0-rc2'
    yield vc, '2.0.0-rc2', '2.0.0-rc3'
    yield vc, '2.0.0-rc2', '2.0.0'
    yield vc, '2.0.0-beta', '2.0.1'


def test_version_check_negative():
    raises(ValueError)(version2array)('1.2.3.4', )
    raises(ValueError)(version2array)('1.2', )
    raises(ValueError)(version2array)('1.2.-beta', )
    raises(ValueError)(version2array)('1.2.3-toto', )
    raises(ValueError)(version2array)('1.2.3-rc', )


class TestUtils(unittest.TestCase):
    def test_formattimedelta(self):
        td = timedelta(0, 60 * 60 + 13 * 60)
        self.assertEqual('1 hours and 13 minutes', format_timedelta(td))

    def test_drawbar(self):
        self.assertEqual(drawbar(5, 10), '[████████▒▒▒▒▒▒▒]')
        self.assertEqual(drawbar(0, 10), '[▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒]')
        self.assertEqual(drawbar(10, 10), '[███████████████]')

    def unescape_test(self):
        self.assertEqual(unescape_xml('&#32;'), ' ')

    def test_storage(self):
        key = b'test' if PY2 else 'test'
        config = sys.modules['errbot.config-template']
        bot_config_defaults(config)

        spm = SpecificPluginManager(config, 'storage', StoragePluginBase, CORE_STORAGE, None)
        storage_plugin = spm.get_plugin_by_name('Memory')

        persistent_object = StoreMixin()
        persistent_object.open_storage(storage_plugin, 'test')
        persistent_object[key] = 'à value'
        self.assertEquals(persistent_object[key], 'à value')
        self.assertIn(key, persistent_object)
        del persistent_object[key]
        self.assertNotIn(key, persistent_object)
        self.assertEquals(len(persistent_object), 0)

    def test_recurse_check_structure_valid(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list=["Foo", "Bar", "Bas"], dict={'foo': "Bar"}, none=None, true=True,
                        false=False)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_missingitem(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_extrasubitem(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list=["Foo", "Bar", "Bas"], dict={'foo': "Bar", 'Bar': "Foo"}, none=None,
                        true=True, false=False)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_missingsubitem(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list=["Foo", "Bar", "Bas"], dict={}, none=None, true=True, false=False)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_wrongtype_1(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string=None, list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_wrongtype_2(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list={'foo': "Bar"}, dict={'foo': "Bar"}, none=None, true=True, false=False)
        recurse_check_structure(sample, to_check)

    @raises(ValidationException)
    def test_recurse_check_structure_wrongtype_3(self):
        sample = dict(string="Foobar", list=["Foo", "Bar"], dict={'foo': "Bar"}, none=None, true=True, false=False)
        to_check = dict(string="Foobar", list=["Foo", "Bar"], dict=["Foo", "Bar"], none=None, true=True, false=False)
        recurse_check_structure(sample, to_check)

    def test_split_string_after_returns_original_string_when_chunksize_equals_string_size(self):
        str_ = 'foobar2000' * 2
        splitter = split_string_after(str_, len(str_))
        split = [chunk for chunk in splitter]
        self.assertEqual([str_], split)

    def test_split_string_after_returns_original_string_when_chunksize_equals_string_size_plus_one(self):
        str_ = 'foobar2000' * 2
        splitter = split_string_after(str_, len(str_) + 1)
        split = [chunk for chunk in splitter]
        self.assertEqual([str_], split)

    def test_split_string_after_returns_two_chunks_when_chunksize_equals_string_size_minus_one(self):
        str_ = 'foobar2000' * 2
        splitter = split_string_after(str_, len(str_) - 1)
        split = [chunk for chunk in splitter]
        self.assertEqual(['foobar2000foobar200', '0'], split)

    def test_split_string_after_returns_two_chunks_when_chunksize_equals_half_length_of_string(self):
        str_ = 'foobar2000' * 2
        splitter = split_string_after(str_, int(len(str_) / 2))
        split = [chunk for chunk in splitter]
        self.assertEqual(['foobar2000', 'foobar2000'], split)
