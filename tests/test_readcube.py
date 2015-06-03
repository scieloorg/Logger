import unittest

from logger import readcube


class ReadCubeBulk(unittest.TestCase):

    def test_instantiating_invalid_len(self):
        sample_line = []

        with self.assertRaises(ValueError):
            am = readcube.AccessMap(sample_line)

    def test_access_map_acesses_invalid_date(self):
        sample_line = ['20X5-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        with self.assertRaises(ValueError):
            am = readcube.AccessMap(sample_line)

    def test_access_map_acesses_day(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.access_day, '27')

    def test_access_map_acesses_month(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.access_month, '05')

    def test_access_map_acesses_year(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.access_year, '2015')

    def test_access_map_acesses_doi(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.doi, '10.1590/S1519-566X2004000500001')

    def test_access_map_acesses_issn(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.issn, '1519-566X')

    def test_access_map_acesses_user_email(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.user_email, 'gmail.com')

    def test_access_map_acesses_user_institution(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.user_institution, 'Seoul National University')

    def test_access_map_acesses_user_role(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.user_role, 'Postdoctoral Fellow')

    def test_access_map_acesses_duration(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', '', '', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.duration, '9')

    def test_access_map_acesses_annotation(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.annotation, 'ann')

    def test_access_map_acesses_highlights(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.highlights, 'highlights')

    def test_access_map_acesses_platform(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.platform, 'web')

    def test_access_map_acesses_ip(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.ip, '147.46.228.216')

    def test_access_map_acesses_country(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.country, 'Republic of Korea')

    def test_access_map_acesses_downloaded(self):
        sample_line = ['2015-05-27T06:29:29.689+00:00', '10.1590/S1519-566X2004000500001', '1519-566X', 'gmail.com', 'Seoul National University', 'Postdoctoral Fellow', '9', 'ann', 'highlights', 'web', '147.46.228.216', 'Republic of Korea', '1']

        am = readcube.AccessMap(sample_line)

        self.assertEqual(am.downloaded, '1')



