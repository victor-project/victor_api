import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_hello_world(self):
        pass



if __name__ == '__main__':
    unittest.main()
