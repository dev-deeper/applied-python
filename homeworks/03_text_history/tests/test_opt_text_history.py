from unittest import TestCase
from text_history import TextHistory, InsertAction, ReplaceAction, DeleteAction


class TextHistoryOptimization(TestCase):

    def test_insert_opt(self):
        h = TextHistory()
        h.insert('a' * 10)
        h.insert('x', pos=3)
        h.insert('yz', pos=4)
        self.assertEqual('aaaxyzaaaaaaa', h.text)
        actions = h.get_actions(1)
        self.assertEqual(1, len(actions))
        action = actions[0]
        self.assertIsInstance(action, InsertAction)
        opt_value = InsertAction(3, 'xyz', 1, 3)
        self.assertEqual(action.__dict__, opt_value.__dict__)

    def test_delete_opt(self):
        h = TextHistory()
        h.insert('a1b2c3d4e5f6g7h8')
        self.assertEqual('a1b2c3d4e5f6g7h8', h.text)
        h.delete(pos=3, length=2)
        self.assertEqual('a1b3d4e5f6g7h8', h.text)
        h.delete(pos=3, length=6)
        self.assertEqual('a1b6g7h8', h.text)
        actions = h.get_actions(1)
        self.assertEqual(1, len(actions))
        action = actions[0]
        self.assertIsInstance(action, DeleteAction)
        opt_value = DeleteAction(3, 8, 1, 3)
        self.assertEqual(action.__dict__, opt_value.__dict__)

