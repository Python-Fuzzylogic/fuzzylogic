from unittest import Test



class DomainTests(unittest.TestCase):

    @unittest.expectedFailure
    def test(self):
        self.fail()

if __name__ == '__main__':
    unittest.main()
