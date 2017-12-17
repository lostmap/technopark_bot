import unittest

import musicgraph1 as mg

import bandsintown1 as bit


class Test(unittest.TestCase):
    def setUp(self):
        self.event = bit.client.search('Lara Fabian', location = 'Moscow, Ru')

    def test_name(self):
        self.assertEqual(self.event[0]['artists'][0]['name'], 'Lara Fabian')

    def test_date(self):
        self.assertEqual(self.event[0]['formatted_datetime'], 'Saturday, February 24, 2018 at 7:00PM')

    def test_location(self):
        self.assertEqual(self.event[0]['venue']['city'], 'Moscow')




if __name__ == "__main__":
    unittest.main()


# event = bit.client.search('Lara Fabian', location = 'Moscow, Ru')
# print(event[0]['venue']['city'])