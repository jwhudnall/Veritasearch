$(document).ready(function() {
	if ($('h2#tweetContainer').length > 0) {
		displayArticles();
	}
	$(window).scroll(function() {
		// if all sections of articles is empty, query getArticles?
	});

	$('#searchForm').on('submit', async function(e) {
		window.name = $('#searchInput').val();
		console.log(`Window name updated: ${window.name}`);
		await getArticles(window.name);
	});
});

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
		localStorage.setItem('articles', JSON.stringify(res.data));
	} catch (e) {
		alert(`Internal API issue Fetching Articles. Error Info: ${e}`);
	}
};

// const getTweets = async function(query) {
// 	try {
// 		// query = $('#searchInput').val();
// 		const res = await axios({
// 			method: 'GET',
// 			url: '/api/tweets',
// 			params: {
// 				q: query
// 			}
// 		});
// 		return res.data;
// 		localStorage.setItem('tweets', JSON.stringify(res.data));
// 	} catch (e) {
// 		alert(`Internal API issue Fetching Tweets. Error Info: ${e}`);
// 	}
// };

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

	// $('#articlesPositive')
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
    <div class="border border-black p-1">
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
