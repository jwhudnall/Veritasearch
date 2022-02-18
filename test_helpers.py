"""Tests for Project Veritas helper functions."""
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgresql:///veritas-test"
from app import categorize_by_sentiment, prune_tweets


class TestHelperFunctions(TestCase):
    """Tests helper functions."""

    def test_categorize_by_sentiment(self):
        """Test categorize_by_sentiment function. Function should return a tuple of 3 lists: Positive, Neutral and Negative sentiment tweets."""

        tweet_lst = [{'id': '1494736886140743686', 'polarity': 0.26, 'sentiment': 'Positive'}, {'id': '1494736662743719945', 'polarity': 0.26, 'sentiment': 'Positive'}, {'id': '1494734710207045635', 'polarity': -0.24, 'sentiment': 'Negative'}, {'id': '1494733468181352455', 'polarity': 0.12, 'sentiment': 'Positive'}, {'id': '1494732183340142592', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494731130171322368', 'polarity': 0.57, 'sentiment': 'Positive'}, {'id': '1494730439176638467', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494729424880680981', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494727012417634305', 'polarity': 0.33, 'sentiment': 'Positive'}, {'id': '1494725957114109958', 'polarity': 0.37, 'sentiment': 'Positive'}, {'id': '1494725913753239555', 'polarity': 0.16, 'sentiment': 'Positive'},
                     {'id': '1494725902609096706', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494725199589089282', 'polarity': -0.03, 'sentiment': 'Negative'}, {'id': '1494724826669277186', 'polarity': 0.07, 'sentiment': 'Positive'}, {'id': '1494724083581263873', 'polarity': 0.25, 'sentiment': 'Positive'}, {'id': '1494722175261020164', 'polarity': 0.3, 'sentiment': 'Positive'}, {'id': '1494722126720425984', 'polarity': -0.05, 'sentiment': 'Negative'}, {'id': '1494720408356012034', 'polarity': -0.12, 'sentiment': 'Negative'}, {'id': '1494719989848461321', 'polarity': 0.15, 'sentiment': 'Positive'}, {'id': '1494718824289120265', 'polarity': 0.13, 'sentiment': 'Positive'}, {'id': '1494718357169479693', 'polarity': 0.4, 'sentiment': 'Positive'}, {'id': '1494718355881660416', 'polarity': -0.25, 'sentiment': 'Negative'}]

        results = categorize_by_sentiment(tweet_lst)
        results_compare = ([{'id': '1494731130171322368', 'polarity': 0.57, 'sentiment': 'Positive'}, {'id': '1494718357169479693', 'polarity': 0.4, 'sentiment': 'Positive'}, {'id': '1494725957114109958', 'polarity': 0.37, 'sentiment': 'Positive'}, {'id': '1494727012417634305', 'polarity': 0.33, 'sentiment': 'Positive'}, {'id': '1494722175261020164', 'polarity': 0.3, 'sentiment': 'Positive'}, {'id': '1494736886140743686', 'polarity': 0.26, 'sentiment': 'Positive'}, {'id': '1494736662743719945', 'polarity': 0.26, 'sentiment': 'Positive'}, {'id': '1494724083581263873', 'polarity': 0.25, 'sentiment': 'Positive'}, {'id': '1494725913753239555', 'polarity': 0.16, 'sentiment': 'Positive'}, {'id': '1494719989848461321', 'polarity': 0.15, 'sentiment': 'Positive'}, {'id': '1494718824289120265', 'polarity': 0.13, 'sentiment': 'Positive'}, {
            'id': '1494733468181352455', 'polarity': 0.12, 'sentiment': 'Positive'}, {'id': '1494724826669277186', 'polarity': 0.07, 'sentiment': 'Positive'}], [{'id': '1494732183340142592', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494730439176638467', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494729424880680981', 'polarity': 0.0, 'sentiment': 'Neutral'}, {'id': '1494725902609096706', 'polarity': 0.0, 'sentiment': 'Neutral'}], [{'id': '1494718355881660416', 'polarity': -0.25, 'sentiment': 'Negative'}, {'id': '1494734710207045635', 'polarity': -0.24, 'sentiment': 'Negative'}, {'id': '1494720408356012034', 'polarity': -0.12, 'sentiment': 'Negative'}, {'id': '1494722126720425984', 'polarity': -0.05, 'sentiment': 'Negative'}, {'id': '1494725199589089282', 'polarity': -0.03, 'sentiment': 'Negative'}])

        self.assertEqual(results, results_compare)

        self.assertEqual(len(results), 3)
        self.assertEqual(len(results[0]), 13)
        self.assertEqual(len(results[1]), 4)
        self.assertEqual(len(results[2]), 5)

        self.assertGreater(results[0][0]['polarity'], 0)
        self.assertEqual(results[1][0]['polarity'], 0)
        self.assertLess(results[2][0]['polarity'], 0)
        # Compare polarity scores within same tuple
        self.assertGreater(results[0][0]['polarity'],
                           results[0][-1]['polarity'])
        self.assertLess(results[2][0]['polarity'],
                        results[2][-1]['polarity'])

        self.assertEqual(results[0][0]['sentiment'], 'Positive')
        self.assertEqual(results[1][0]['sentiment'], 'Neutral')
        self.assertEqual(results[2][0]['sentiment'], 'Negative')

    def test_prune_tweets(self):
        """Test prune_tweets function. Function prunes a list of raw_tweet objects to contain a specified list of key:value pairs.

        Keys to be returned: id, text, polarity, sentiment, embed_html
        """
        raw_tweets = [
            {'created_at': 'Sun Feb 13 22:56:43 +0000 2022', 'id': 1492996182670462980, 'id_str': '1492996182670462980', 'full_text': 'If the Bengals win the Super Bowl I’m giving one person who likes and retweets this tweet $10,000 dollars.\n\nMust be following me to win. GO.', 'truncated': False, 'display_text_range': [0, 140], 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}, 'metadata': {'result_type': 'popular', 'iso_language_code': 'en'}, 'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 581301629, 'id_str': '581301629', 'name': 'Jake Paul', 'screen_name': 'jakepaul', 'location': 'United States', 'description': '', 'url': 'https://t.co/HyYBC352W9', 'entities': {'url': {'urls': [{'url': 'https://t.co/HyYBC352W9', 'expanded_url': 'http://www.showtime.com/ppv', 'display_url': 'showtime.com/ppv', 'indices': [0, 23]}]}, 'description': {'urls': []}}, 'protected': False, 'followers_count': 4291573, 'friends_count': 8727, 'listed_count': 2183, 'created_at': 'Tue May 15 22:26:56 +0000 2012', 'favourites_count': 8957, 'utc_offset': None, 'time_zone': None,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       'geo_enabled': True, 'verified': True, 'statuses_count': 11521, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'C0DEED', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1459728843531509763/f1S6_nQp_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1459728843531509763/f1S6_nQp_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/581301629/1640406672', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': False, 'following': None, 'follow_request_sent': None, 'notifications': None, 'translator_type': 'none', 'withheld_in_countries': []}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 126264, 'favorite_count': 170646, 'favorited': False, 'retweeted': False, 'lang': 'en'}
        ]

        result_v1 = prune_tweets(raw_tweets, 'id_str', 'full_text')

        self.assertEqual(result_v1[0], {
                         'id': '1492996182670462980', 'polarity': 0.32, 'sentiment': 'Positive'})
        self.assertIn('id', result_v1[0])
        self.assertIn('polarity', result_v1[0])
        self.assertIn('sentiment', result_v1[0])
        self.assertEqual(len(result_v1[0].keys()), 3)

    # def test_remove_stop_words(self):
    #     """Test remove_stop_words function. Uses nltk to remove stop words, returning a string of n words. """

    #     raw_sentence = "This is a sentence that includes stop words."

    #     result_1 = remove_stop_words(raw_sentence)
    #     self.assertEqual(result_1, 'This sentence')
    #     result_2 = remove_stop_words(raw_sentence, n=3)
    #     self.assertEqual(result_2, 'This sentence includes')
