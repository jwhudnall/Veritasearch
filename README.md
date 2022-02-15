# Project Veritas
*Discover Truth.*

Veritas is an attempt to aggregate and classify information based on it's underlying sentiment. The goal is to provide information to the user that is clearly labelled, in an effort to increase transparency and reduce echo chambers. The first iteration uses the Twitter platform as an information source.

## How it Works
Users search a topic using the main search bar. The search query is then url-encoded and sent to Twitter's API, first looking for an acceptable amount of tweets classified as "Popular." If too few results are returned, the Twitter API is re-queried to search for all tweets related to the user's query.

Once results are returned, they are then pruned to remove superfluous fields. Each returned tweet's id is then sent to Twitter's oEmbed API, yielding an embedded html code block to be used later when rendering tweets. The text from each tweet is then sent to a Machine Learning Natural Language Processing API, which returns a sentiment score. Together, these fields are aggregated to construct and return a list of unassigned tweet objects.

The pruned tweets are then categorized into 3 distinct sentiment groups, sorted by their polarity score. This categorized list is then passed to the search result page, rendering clearly-labelled information to the user.

If a user has an account and is signed in, their search queries are saved and used to display recommended information based on their search history. User's have the ability to delete individual queries, which in turn removes related tweets from their recommendation page.


## API's Used
- [Twitter (Standard v1.1)](https://developer.twitter.com/en/docs/api-reference-index#twitter-api-standard)
- [Twitter oEmbed API](https://developer.twitter.com/en/docs/twitter-for-websites/oembed-api#Embedded)
- [Sentim](https://sentim-api.herokuapp.com/)
  - This API was chosen due to it's simplicity, speed and consistent performance. It has a great web interface for testing text input. Querying the actual API was just as seamless.