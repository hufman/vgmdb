import unittest

class TestFalse(unittest.TestCase):
	def setUp(self):
		pass

	def test_false(self):
		self.assertFalse(False)

