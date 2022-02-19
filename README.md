# Project Veritas

_Discover Truth._

<img src="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/static/images/veritas-search-home.jpg?raw=true" alt="Veritas Search Homepage" width="400px">

Veritas is an attempt to aggregate and classify information based on it's underlying sentiment. The goal is to provide information to the user that is clearly labelled, in an effort to increase transparency and reduce echo chambers. The first iteration uses the Twitter platform as an information source.

Live link: http://www.veritasearch.com/

Original Proposal: <a href="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/Project%20Veritas%20-%20Capstone%201%20Project%20Proposal.pdf">Project Veritas - Project Proposal.pdf</a>

<hr>

## How it Works

The backend is implemented with python and served via Flask. Users are guided to search a topic using one of the main search bars. The search query is then sent to the <a href="https://developer.twitter.com/en/docs/twitter-api">Twitter API v2</a>, returning tweets related to the user's query. The search is optimized to exclude retweets, and source tweets from verified accounts only.

Once results are returned, they are pruned to remove superfluous fields. The text from each tweet is then sent to <a href="https://sentim-api.herokuapp.com/">Sentim API</a>, a Machine Learning Natural Language Processing tool that returns a sentiment and polarity score. Together, these fields are aggregated to construct and return a list of unordered tweet objects. The list of unordered tweets is then categorized into a tuple comprised of 3 buckets; Positives, Neutrals and Negatives, sorted by polarity score.

This tuple is served from Flask on the backend to Javascript on the front end, where each tweet id is used to leverage <a href="https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/scripting-factory-functions">Twitter's Javascript API</a> to render tweets in their familiar form. Sentiment labels with the overall sentiment and polarity score is also created and added atop each resulting tweet, rendering clearly-labelled information to the user.

If a user has an account and is signed in, their search queries are saved and used to display recommended information based on their search history. User's have the ability to delete individual queries, which in turn affects their recommendations.

<hr>

## Standard User Flow

1. A user lands on the page, and enters a search term (most likely from a pre-selected option).
2. After reviewing the results, the user is gently encouraged to create an account in order to receive personalized recommendations.
3. Once a user registers, any queries they make will be tied to their account. When they visit their profile page, they will be able to click a button to receive recommendations. Currently, these recommendations are a search for randomized variants of previous user-queries. The end result is categorized content from more than one topic.
4. From their profile page, users can delete individual queries. Doing so removes related searches as potential recommendation material.
5. Users can also delete their account from a drop-down accordion, removing all queries tied to their account.
<hr>

## Main Features

- **Side-by-Side Viewpoint Perspective** - On desktop, results are presented side-by-side. The goal is to present different perspectives through which the user can search:
  <img src="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/static/images/readme-images/veritas-results.jpg?raw=true" alt="Veritas Search Results" width="250px">

- **Suggested Searches** - I use python to randomly select 3 search-topics from a predefined list. Users can click a suggestion to trigger a search of that topic. I implemented this to reduce friction when users are first introduced to the platform:
  <img src="https://raw.githubusercontent.com/jwhudnall/Springboard-Capstone-1/main/static/images/readme-images/veritas-suggested-searches.jpg" alt="Veritas Search Suggestions" width="250px">

- **How it Works Section** - I added this to help the user understand what was going on behind the scenes. I believe it's a good high-level overview for those that don't read this documentation:

  <img src="https://raw.githubusercontent.com/jwhudnall/Springboard-Capstone-1/main/static/images/readme-images/veritas-how-it-works.jpg" alt="Veritas How it Works" width="250px">

- **Personal Recommendations** - This was implemented to offer the user incentive to continue using the platform. Recommendations are based on previous queries:
  <img src="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/static/images/readme-images/veritas-recommendations.jpg?raw=true" alt="Veritas Search Suggestions" width="250px">

- **Past Search Removal Options** - I felt it important that the user be able to remove past searches:

  <img src="https://raw.githubusercontent.com/jwhudnall/Springboard-Capstone-1/main/static/images/readme-images/veritas-query-removal.jpg" alt="Veritas Search Deletion" width="250px">

- **Account Removal** - I also felt it important that the user could delete their account, removing any trace of information related to their searches:
  <img src="https://raw.githubusercontent.com/jwhudnall/Springboard-Capstone-1/main/static/images/readme-images/veritas-delete-account.jpg" alt="Veritas Account Removal" width="250px">

- **Login and Register Modals** - I felt like this gave the site a more professional feel, vs the standard landing page for login and registration handling:
<img src="https://github.com/jwhudnall/Springboard-Capstone-1/blob/main/static/images/readme-images/veritas-modals.jpg?raw=true" alt="Veritas Sign In Modal" width="250px">
<hr>

## API's Used

- <a href="https://developer.twitter.com/en/docs/twitter-api">Twitter API v2</a>
  - I originally planned to use Twitter's v1 API (which retrieves tweets Twitter classifies as "popular"). During implementation, however, I realized the results were very limited. I migrated to v2 to facilitate wider viewpoints.
- <a href="https://developer.twitter.com/en/docs/twitter-for-websites/javascript-api/guides/scripting-factory-functions">Twitter's Javascript API</a>
  - I originally served embedded HTML for each tweet via Flask/Jinja. However, after a bit of experimentation, I discovered the Javascript implementation <ins>**reduced rendering time by as much as 80%**</ins> in some cases.
- <a href="https://sentim-api.herokuapp.com/">Sentim API</a>
  - This API was chosen due to it's simplicity, speed and consistent performance. It has a great web interface for testing text input. Querying the actual API was just as seamless.

The styling was implemented via <a href="https://tailwindcss.com/">TailwindCSS</a>.

<hr>

## Lessons Learned

1. **Read the Docs**. I originally planned to serve news articles, in addition to Tweets. Midway during the development cycle, I started becoming rate-limited with news queries. After closer inspection of the News API docs, I learned that my application would only be able to query articles 100 times in a 24-hour period. The alternative? $500 a month. I decided to forgo the news article aspect, savings costs and allowing me to narrow my focus on the tweet pipeline.

2. **Have Strong Opinions, Loosely Held**. I bounced back and forth between implementing different aspects using Python and Javascript. While this taught me a lot about how I could do things multiple ways, it also taught me that I needed to experiment, but then be decisive in landing on an implementation strategy.
