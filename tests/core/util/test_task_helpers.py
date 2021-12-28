from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock, Mock

from fsstalker.core.db.db_models import Watch
from fsstalker.core.util.task_helpers import submission_type_filter, checked_submission_filter, \
    check_submission_for_watches, check_watches


class TestTaskHelpers(TestCase):
    def test_submission_type_filter(self):
        subs = [
            MagicMock(is_self=False, post_hint='image', id=1),
            MagicMock(is_self=True, id=2),
            MagicMock(is_self=False, post_hint='video', id=3)
        ]

        r = list(filter(submission_type_filter('text'), subs))
        self.assertTrue(len(r) == 1)
        self.assertEqual(2, r[0].id)


    def test_checked_submission_filter(self):
        # Faking a db call checking if object exists
        def return_checked(id):
            if id == 2:
                return False
            else:
                return True

        checked_repo = MagicMock()
        uow = MagicMock()
        uowm = MagicMock()
        checked_repo.get_by_post_id.side_effect = return_checked
        type(uow).checked_post = PropertyMock(return_value=checked_repo)
        uow.__enter__.return_value = uow
        uowm.start.return_value = uow

        subs = [
            Mock(id=1),
            Mock(id=2),
            Mock(id=3)
        ]

        r = list(filter(checked_submission_filter(uowm), subs))
        self.assertTrue(len(r) == 1)
        self.assertEqual(2, r[0].id)

    def test_check_submission_for_watches_return_none(self):
        watches = [
            Watch(id=1, include='8tb'),
            Watch(id=2, include='test'),
            Watch(id=3, include='other')
        ]
        r = check_submission_for_watches(Mock(selftext='Some non-matching thing', title='random title'), watches)
        self.assertIsNone(r)

    def test_check_submission_exclude_lower_for_watches_return_none(self):
        watches = [
            Watch(id=1, include='8tb', exclude='[W]'),
            Watch(id=2, include='test'),
            Watch(id=3, include='other')
        ]
        r = check_submission_for_watches(Mock(selftext='Some matching thing 8tb', title='[w] random title'), watches)
        self.assertIsNone(r)

    def test_check_submission_for_watches_return_8tb(self):
        watches = [
            Watch(id=1, include='8tb'),
            Watch(id=2, include='test'),
            Watch(id=3, include='other')
        ]
        submission = Mock(selftext='Some matching thing 8tb', title='random title')
        r = check_submission_for_watches(submission, watches)
        self.assertIsNotNone(r)
        self.assertDictEqual(r, {'watch_id': 1, 'match_word': '8tb', 'submission': submission})

    @patch('fsstalker.core.util.task_helpers.create_checked_post')
    def test_check_watches_created_checked_post(self, patch_checked):
        patch_checked.return_value = None
        watch_repo = MagicMock()
        uow = MagicMock()
        uowm = MagicMock()
        watch_repo.get_by_post_id.return_value = [Watch(id=1, include='8tb')]
        type(uow).checked_post = PropertyMock(return_value=watch_repo)
        uow.__enter__.return_value = uow
        uowm.start.return_value = uow
        check_watches(uowm, [Mock(selftext='Some body', title='some title')])
        patch_checked.assert_called()

    @patch('fsstalker.core.util.task_helpers.create_checked_post')
    def test_check_watches_created_checked_post(self, patch_checked):
        patch_checked.return_value = None
        watch_repo = MagicMock()
        uow = MagicMock()
        uowm = MagicMock()
        watch_repo.get_by_subreddit.return_value = [Watch(id=1, include='8tb')]
        type(uow).watch = PropertyMock(return_value=watch_repo)
        uow.__enter__.return_value = uow
        uowm.start.return_value = uow
        submissions = [Mock(selftext='Some body 8tb', title='some title', subreddit=Mock(display_name='test'))]
        r = check_watches(uowm, submissions)
        expected = {'watch_id': 1, 'match_word': '8tb', 'submission': submissions[0]}
        self.assertIsNotNone(r)
        self.assertDictEqual(r[0], expected)
