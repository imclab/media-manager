from __future__ import unicode_literals
from __future__ import print_function
import os
import shutil
import tempfile
import unittest

from pkg_resources import resource_filename

from media_manager import metadata
from media_manager import sourcerepo
from media_manager import utils


class ChdirContext(object):
    """Context manager for a 'with' loop."""
    def __init__(self, target):
        self._original = os.getcwd()
        self._target = target

    def __enter__(self):
        os.chdir(self._target)
        return self

    def __exit__(self, *args):
        os.chdir(self._original)
        return self


class SourceRepoTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.source_repo = sourcerepo.SourceRepo(self.tempdir)
        # Two sample images from 2011.
        self.sample_img1 = resource_filename(
            'media_manager.tests', 'images/IMG_1285.JPG')
        self.sample_img2 = resource_filename(
            'media_manager.tests', 'images/IMG_1306.JPG')
        # One sample image from 2012.
        self.sample_img3 = resource_filename(
            'media_manager.tests', 'images/IMG_0337.JPG')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_ensure_directory1(self):
        self.source_repo.ensure_directory('photos')
        self.assertTrue(utils.exists(self.tempdir, 'photos'))

    def test_ensure_directory2(self):
        self.source_repo.ensure_directory('photos', 1972)
        self.assertTrue(utils.exists(self.tempdir, 'photos', '1972'))

    def test_ensure_directory3(self):
        self.source_repo.ensure_directory('photos', '1972')
        self.assertTrue(utils.exists(self.tempdir, 'photos', '1972'))

    def test_ensure_directory4(self):
        self.assertRaises(AssertionError,
                          self.source_repo.ensure_directory,
                          'something_else')

    def test_add_file1(self):
        sample_file = metadata.Photo(
            original_filepath=self.sample_img1,
            year=2011)
        self.source_repo.add_file(sample_file)
        self.assertTrue(utils.exists(self.tempdir,
                                     'photos/2011/img_1285.jpg'))

    def test_add_file2(self):
        sample_file = metadata.Photo(
            original_filepath=self.sample_img3,
            year=2012)
        self.source_repo.add_file(sample_file)
        self.assertTrue(utils.exists(self.tempdir,
                                     'photos/2012/img_0337.jpg'))

    def test_add_file_git_integration(self):
        sample_file = metadata.Photo(
            original_filepath=self.sample_img3,
            year=2012)
        self.source_repo.add_file(sample_file)
        self.assertTrue(self.source_repo.git_commands,
                        ['git annex add photos/2012/img_0337.jpg'])

    def test_add_file_sets_id(self):
        sample_file = metadata.Photo(
            original_filepath=self.sample_img1,
            year=2011)
        self.source_repo.add_file(sample_file)
        self.assertEquals(sample_file.id, 'photos/2011/img_1285.jpg')

    def test_add_file_with_title(self):
        sample_file = metadata.Photo(
            original_filepath=self.sample_img1,
            year=2011,
            title="Some nice title")
        self.source_repo.add_file(sample_file)
        self.assertTrue(utils.exists(self.tempdir,
                                     'photos/2011/some-nice-title.jpg'))
        self.assertEquals(sample_file.id, 'photos/2011/some-nice-title.jpg')

    def test_add_file_with_title_with_duplicates(self):
        sample_file1 = metadata.Photo(
            original_filepath=self.sample_img1,
            year=2011,
            title="Some nice title")
        sample_file2 = metadata.Photo(
            original_filepath=self.sample_img2,
            year=2011,
            title="Some nice title")
        self.source_repo.add_file(sample_file1)
        self.source_repo.add_file(sample_file2)
        self.assertTrue(utils.exists(self.tempdir,
                                     'photos/2011/some-nice-title.jpg'))
        self.assertTrue(utils.exists(self.tempdir,
                                     'photos/2011/some-nice-title_.jpg'))
        self.assertEquals(sample_file1.id, 'photos/2011/some-nice-title.jpg')
        self.assertEquals(sample_file2.id, 'photos/2011/some-nice-title_.jpg')


class SourceRepoWithAnnexTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        with ChdirContext(self.tempdir):
            os.system("git init")
            os.system("git annex init tempdir")
        self.source_repo = sourcerepo.SourceRepo(self.tempdir)
