from unittest import TestCase
from unittest.mock import MagicMock

from fsstalker.core.util.helpers import get_submission_type, post_includes_words


class TestHelpers(TestCase):
    def test_get_submission_type_missing_key_return_none(self):
        self.assertIsNone(get_submission_type(MagicMock(is_self=False)))

    def test_get_submission_type_self_text_return_text(self):
        self.assertEqual('text', get_submission_type(MagicMock(is_self=True)))

    def test_get_submission_type_post_hint_return_image(self):
        self.assertEqual('image', get_submission_type(MagicMock(is_self=False, post_hint='image')))

    def test_post_includes_words_return_word(self):
        text = 'This is some long post about selling an 8tb hard drive'
        words = ['thing', '8tb', 'other thing']
        self.assertEqual('8tb', post_includes_words(words, text))

    def test_post_includes_words_upper_case_return_word(self):
        text = 'This is some long post about selling an 8TB hard drive'
        words = ['thing', '8tb', 'other thing']
        self.assertEqual('8tb', post_includes_words(words, text))

    def test_post_exclude_words_upper_case_return_None(self):
        text = '[w] This is some long post about selling an 8TB hard drive'
        words = ['thing', '8tb', 'other thing']
        exclude_words = ['[W]']
        self.assertIsNone(post_includes_words(words, text, exclude_words=exclude_words))

    def test_post_includes_words_exclude_return_none(self):
        text = 'This is some long post about selling an 8tb hard drive'
        words = ['thing', '8tb', 'other thing']
        self.assertIsNone(post_includes_words(words, text, exclude_words=['selling']))

    def test_post_includes_words_return_none(self):
        text = 'This is some long post about selling an 8tb hard drive'
        words = ['thing', 'other thing']
        self.assertIsNone(post_includes_words(words, text))