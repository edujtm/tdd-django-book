from django.test import TestCase

# Create your tests here.

class SmokeTest(TestCase):

  def test_quick_maths(self):
    self.assertEqual(2+2, 3)