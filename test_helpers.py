"""Tests for Project Veritas helper functions."""
from unittest import TestCase
from app import categorize_tweets, prune_articles


class TestHelperFunctions(TestCase):
    """Tests helper functions."""

    def test_categorize_tweets(self):
        tweet_lst = [
            {
                'id': '1490818219015294976',
                'type': 'tweet',
                'url': 'https://t.co/A2Ct4d8RmB',
                'published': 'Mon Feb 07 22:42:16 +0000 2022',
                'source': 'The Lead CNN',
                'text': '"The transatlantic partnership ...',
                'is_truncated': False,
                'polarity': 0.14,
                'sentiment': 'positive'
            },
            {
                'id': '1490966801844674560',
                'type': 'tweet',
                'url': 'https://t.co/wMUm6ArICz',
                'published': 'Tue Feb 08 08:32:41 +0000 2022',
                'source': 'Olaf Scholz',
                'text': 'Everyone can be absolutely sure that Germany...',
                'is_truncated': False,
                'polarity': 0.06,
                'sentiment': 'positive'},
            {
                'id': '1490790301132333057',
                'type': 'tweet',
                'url': 'https://t.co/KzSv3OKU98',
                'published': 'Mon Feb 07 20:51:19 +0000 2022',
                'source': 'Katie Pavlich',
                'text': 'As the White House insists Russia could invade Ukraine...',
                'is_truncated': False,
                'polarity': 0.0,
                'sentiment': 'neutral'
            },
            {
                'id': '1490929799589949440',
                'type': 'tweet',
                'url': 'https://t.co/MGIxU8Ase4',
                'published': 'Tue Feb 08 06:05:39 +0000 2022',
                'source': 'AFP News Agency',
                'text': 'Ukraine-Russia military balance.\n\n#AFPgraphics...',
                'is_truncated': False,
                'polarity': -0.03,
                'sentiment': 'negative'}
        ]
        results = categorize_tweets(tweet_lst)

        self.assertEqual(len(results), 3)
        self.assertEqual(len(results[0]), 2)
        self.assertEqual(len(results[1]), 1)
        self.assertEqual(len(results[2]), 1)

    def test_prune_articles(self):
        articles = [
            {'source': {'id': None, 'name': 'Yahoo Entertainment'},
             'author': 'Yaёl Bizouati-Kennedy',
             'title': 'Bitcoin Payroll: The Future of Hiring? Crypto Benefits Plan Could Attract Workers and Improve Employee Retention, Survey Says',
             'description': 'The Great Resignation triggered a talent war and a very tight labor market, pushing employers to reconsider perks they offer. Now, a new survey suggests that...',
             'url': 'https://finance.yahoo.com/news/bitcoin-payroll-future-hiring-crypto-170144369.html',
             'urlToImage': 'https://s.yimg.com/ny/api/res/1.2/mrjL.xbq5kQ6_DLCm9bS.Q--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD02NzU-/https://s.yimg.com/uu/api/res/1.2/meOGCSd2QYWgkuvNNvP9wQ--~B/aD0xMDgwO3c9MTkyMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/gobankingrates_644/89cba59bc2f89b45d9b5eb426b93ee83',
             'publishedAt': '2022-02-10T17:01:44Z',
             'content': 'The Great Resignation triggered a talent war and a very tight labor market, pushing employers to reconsider perks they offer. Now, a new survey suggests that nearly one in four workers would prefer a… [+3329 chars]'}
        ]

        result = prune_articles(articles)

        self.assertEqual(len(result), 1)
        # Check for presence of all keys, sentiment
