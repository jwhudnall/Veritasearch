# Project Veritas

_Discover Truth._

<img src="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/static/images/veritas-search-home.jpg?raw=true" alt="Veritas Search Homepage" width="400px">

Veritas is an attempt to aggregate and classify information based on it's underlying sentiment. The goal is to provide information to the user that is clearly labelled, in an effort to increase transparency and reduce echo chambers. The first iteration uses the Twitter platform as an information source.

Live link: http://www.veritasearch.com/

## How it Works

The backend is implemented with python and served via Flask. Users are guided to search a topic using one of the main search bars. The search query is then sent to the <a href="https://developer.twitter.com/en/docs/twitter-api">Twitter API v2</a>, returning tweets related to the user's query. The search is optimized to exclude retweets, and source tweets from verified accounts only.

Once results are returned, they are pruned to remove superfluous fields. The text from each tweet is then sent to <a href="https://sentim-api.herokuapp.com/">Sentim API</a>, a Machine Learning Natural Language Processing tool that returns a sentiment and polarity score. Together, these fields are aggregated to construct and return a list of unordered tweet objects. The list of unordered tweets is then categorized into a tuple comprised of 3 buckets; Positives, Neutrals and Negatives, sorted by polarity score.

This tuple is served from Flask on the backend to Javascript on the front end, where each tweet id is used to leverage <a href="https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/scripting-factory-functions">Twitter's Javascript API</a> to render tweets in their familiar form. Sentiment labels with the overall sentiment and polarity score is also created and added atop each resulting tweet, rendering clearly-labelled information to the user.

If a user has an account and is signed in, their search queries are saved and used to display recommended information based on their search history. User's have the ability to delete individual queries, which in turn affects their recommendations.

## Standard User Flow

1. A user lands on the page, and enters a search term (most likely from a pre-selected option).
2. After reviewing the results, the user is gently encouraged to create an account in order to receive personalized recommendations.
3. Once a user registers, any queries they make will be tied to their account. When they visit their profile page, they will be able to click a button to receive recommendations. Currently, these recommendations are a search for randomized variants of previous user-queries. The end result is categorized content from more than one topic.
4. From their profile page, users can delete individual queries. Doing so removes related searches as potential recommendation material.
5. Users can also delete their account from a drop-down accordion, removing all queries tied to their account.

## Main Features

- **Side-by-Side Viewpoint Perspective** - On desktop, results are presented side-by-side. The goal is to present different perspectives through which the user can search:

- **Suggested Searches** - I use python to randomly select 3 search-topics from a predefined list. Users can click a suggestion to trigger a search of that topic. I implemented this to reduce friction when users are first introduced to the platform:

- **How it Works Section** - I added this to help the user understand what was going on behind the scenes:

- **Personal Recommendations** - This was implemented to offer the user incentive to continue using the platform. Recommendations are based on previous queries:

- **Personal Search Removal Options** - I felt it important that the user be able to remove past searches:

- **Account Removal** - I also felt it important that the user could delete their account, removing any trace of information related to their searches:

## API's Used

- <a href="https://developer.twitter.com/en/docs/twitter-api">Twitter API v2</a>
- <a href="https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/scripting-factory-functions">Twitter's Javascript API</a>
- <a href="https://sentim-api.herokuapp.com/">Sentim API</a>
  - This API was chosen due to it's simplicity, speed and consistent performance. It has a great web interface for testing text input. Querying the actual API was just as seamless.
