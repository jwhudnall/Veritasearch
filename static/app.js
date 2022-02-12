const positiveTweetContainer = document.getElementById('tweetsPositive');
const neutralTweetContainer = document.getElementById('tweetsNeutral');
const negativeTweetContainer = document.getElementById('tweetsNegative');
const positiveArticleContainer = document.getElementById('articlesPositive');
const neutralArticleContainer = document.getElementById('articlesNeutral');
const negativeArticleContainer = document.getElementById('articlesNegative');

$(document).ready(async function() {
	$('#searchResultContainer').hide();
	if ($('#searchResultContainer').length > 0) {
		// Tweets
		if (localStorage.articles == undefined || localStorage.tweets == undefined) {
			fetchAndShowContent();
		} else {
			alert('LocalStorage exists. Retrieving data...');
			$('#searchResultContainer').show();
			displayArticles();
			renderEmbedTweets();
		}
	}

	$('#headlineWords').on('click', 'span', async function() {
		localStorage.clear();
		query = $(this).text();
		window.name = $('#searchInput').val(query);
		$('#searchForm').submit();
	});

	$('#searchForm').on('submit', async function(e) {
		window.name = $('#searchInput').val();
		localStorage.clear();
	});
});

const fetchAndShowContent = async function() {
	$('#searchResultContainer').hide();
	showLoadingView();
	await getArticles(window.name);
	$('#searchResultContainer').show();
	displayArticles();
	// await getTweets(window.name);
	tweets = await getEmbedTweets(window.name);
	// renderTweets();
	renderEmbedTweets();
	await twttr.widgets.load();
	hideLoadingView();
};

const showLoadingView = function() {
	$('#searchBtn').text('Searching...').prop('disabled', true);
	const $loadingIcon = $('<img>')
		.attr({ src: '/static/images/loading-icon.jpeg', id: 'loadingImg' })
		.addClass('w-32 mx-auto mt-5');
	$loadingIcon.insertBefore($('#searchResultContainer'));
};

const hideLoadingView = function() {
	$('#loadingImg').remove();
	$('#searchBtn').text('Search').prop('disabled', false);
};

const asyncLocalStorage = {
	setItem: async function(key, value) {
		await null;
		return localStorage.setItem(key, value);
	},
	getItem: async function(key) {
		await null;
		return localStorage.getItem(key);
	}
};

const getArticles = async function(query) {
	try {
		// query = $('#searchInput').val();
		const res = await axios({
			method: 'GET',
			url: '/api/articles',
			params: {
				q: query
			}
		});
		// return res.data;
		if (res.data.error) {
			console.log('No articles found!');
			return;
		}
		asyncLocalStorage.setItem('articles', JSON.stringify(res.data));
	} catch (e) {
		alert(`Internal API issue Fetching Articles. Error Info: ${e}`);
	}
};

const getEmbedTweets = async function(query) {
	try {
		const res = await axios({
			method: 'GET',
			url: '/api/tweets',
			params: {
				q: query
			}
		});
		if (res.data.error) {
			console.log('No tweets found!');
			return;
		}
		asyncLocalStorage.setItem('tweets', JSON.stringify(res.data));
		console.log('localStorage["tweets"] updated!');
		console.dir(res.data);
	} catch (e) {
		alert(`Internal API issue Fetching Tweets. Error Info: ${e}`);
	}
};

const getTweets = async function(query) {
	try {
		const res = await axios({
			method: 'GET',
			url: '/api/tweets',
			params: {
				q: query
			}
		});
		if (res.data.error) {
			console.log('No tweets found!');
			return;
		}
		asyncLocalStorage.setItem('tweets', JSON.stringify(res.data));
		console.log('localStorage["tweets"] updated!');
		// return res.data;
	} catch (e) {
		alert(`Internal API issue Fetching Tweets. Error Info: ${e}`);
	}
};

const retrieveTwitterCard = async function(id, maxWidth = 220, omitScript = false, hideMedia = false) {
	try {
		const res = await axios({
			method: 'GET',
			url: 'https://publish.twitter.com/oembed',
			params: {
				url: `https://twitter.com/Interior/status/${id}`,
				maxwidth: maxWidth,
				hide_media: hideMedia,
				omit_script: omitScript
			}
		});
		console.dir(res);
		return res.data;
	} catch (e) {
		alert(`Issue fetching Twitter Cards. Error info: ${e}`);
	}
};

const renderEmbedTweets = function() {
	tweets = JSON.parse(localStorage.getItem('tweets')).tweets;
	const positive = tweets[0];
	const neutral = tweets[1];
	const negative = tweets[2];

	if (positive.length > 0) {
		for (let t of positive) {
			appendTweet(t, positiveTweetContainer);
		}
	}
	if (neutral.length > 0) {
		for (let t of neutral) {
			appendTweet(t, neutralTweetContainer);
		}
	}
	if (negative.length > 0) {
		for (let t of negative) {
			appendTweet(t, negativeTweetContainer);
		}
	}
};

// const renderTweets = function() {
// 	tweets = JSON.parse(localStorage.getItem('tweets')).tweets;
// 	const positive = tweets[0];
// 	const neutral = tweets[1];
// 	const negative = tweets[2];

// 	if (positive.length > 0) {
// 		for (let t of positive) {
// 			appendTweet(t.id, positiveTweetContainer);
// 		}
// 	}
// 	if (neutral.length > 0) {
// 		for (let t of neutral) {
// 			appendTweet(t.id, neutralTweetContainer);
// 		}
// 	}
// 	if (negative.length > 0) {
// 		for (let t of negative) {
// 			appendTweet(t.id, negativeTweetContainer);
// 		}
// 	}
// };

const appendTweet = function(tweet, targetEl) {
	const container = document.createElement('div');
	const tweetCard = document.createElement('div');
	const sentDiv = document.createElement('div');
	const polarity = document.createElement('span');
	polarity.innerText = `Score: ${tweet.polarity}`;
	sentDiv.append(polarity);
	tweetCard.innerHTML = tweet.oembed_url;
	container.append(sentDiv, tweetCard);
	targetEl.append(container);
};

const appendTweetWidget = function(id, targetEl) {
	twttr.widgets.createTweet(id, targetEl, {
		cards: 'hidden'
	});
};

// const createAndAppendTweetHTML = function(tweet, targetEl) {
// 	const container = document.createElement('div');
// 	const tweetCard = document.createElement('div');
// 	const sentDiv = document.createElement('div');
// 	const polarity = document.createElement('span');
// 	polarity.innerText = `Score: ${tweet.polarity}`;
// 	sentDiv.append(polarity);
// 	tweetCard.innerHTML = tweet.oembed_url;
// 	container.append(sentDiv, tweetCard);
// 	targetEl.append(container);
// }

const displayArticles = function() {
	articles = JSON.parse(localStorage.getItem('articles')).articles;
	const positive = articles[0];
	const neutral = articles[1];
	const negative = articles[2];

	if (positive.length > 0) {
		for (let a of positive) {
			appendArticle(a, 'positive');
		}
	}
	if (neutral.length > 0) {
		// append all neutral articles
		for (let a of neutral) {
			appendArticle(a, 'neutral');
		}
	}
	if (negative.length > 0) {
		// append all negative articles
		for (let a of negative) {
			appendArticle(a, 'negative');
		}
	}
};

const appendArticle = function(article, sentKey) {
	let targetTag;
	const sentKeys = {
		positive: 'Positive',
		neutral: 'Neutral',
		negative: 'Negative'
	};

	if (sentKey.length > 0) {
		targetTag = `articles${sentKeys[sentKey]}`;
	}

	const newArticle = $(`
    <div class="border border-black p-1 text-sm">
      <h2>${article.title}</h2>
      <p>${article.description}</p>
      <p class="text-xs font-medium">Polarity: ${article.polarity}</p>
      <div class="text-xs">
        <span>By ${article.source}</span>
        <span> on ${article.published}</span>
      </div>
    </div>
  `);

	$(`#${targetTag}`).append(newArticle);
};
