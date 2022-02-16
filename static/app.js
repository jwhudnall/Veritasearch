// const positiveTweetContainer = document.getElementById('tweetsPositive');
// const neutralTweetContainer = document.getElementById('tweetsNeutral');
// const negativeTweetContainer = document.getElementById('tweetsNegative');
// const positiveArticleContainer = document.getElementById('articlesPositive');
// const neutralArticleContainer = document.getElementById('articlesNeutral');
// const negativeArticleContainer = document.getElementById('articlesNegative');

$(document).ready(async function () {
  if ($("#searchResultContainer").length > 0) {
    const $divs = $(".fade-in-div");
    console.log("Page loaded!");
    $divs.hide();
    showLoadingView($divs, "tweetDivs");
    setTimeout(function () {
      $divs.show();
      hideLoadingView("tweetDivs");
    }, 3000);
    console.log("Divs Rendered!");

    // twttr.widgets.load(
    // 	document.getElementById('searchResultContainer')
    // );

    // if (localStorage.articles == undefined || localStorage.tweets == undefined) {
    // 	fetchAndShowContent();
    // } else {
    // 	displayArticles();
    // 	renderEmbedTweets();
    // }
  }

  // 	$('#headlineWords').on('click', 'span', async function() {
  // 		localStorage.clear();
  // 		query = $(this).text();
  // 		window.name = $('#searchInput').val(query);
  // 		$('#searchForm').submit();
  // 	});

  $(".veritasSearchForm").on("submit", renderSearchLoading);

  $("#queryContainer").on("click", "button", deleteQuery);
  $("#delActBtn").on("click", deleteAccount);

  $("#headlineWords").on(
    "click",
    ".veritasSearchSuggestion",
    renderSearchLoading
  );
});

const showLoadingView = function ($targetEl, tag) {
  // $("#searchBtn").text("Searching...").prop("disabled", true);
  const $loadingIcon = $("<img>")
    .attr({
      src: "/static/images/loading-icon.jpeg",
      class: `loadingImg${tag}`,
    })
    .addClass("w-32 mx-auto mt-5");
  $loadingIcon.insertAfter($targetEl);
};

const hideLoadingView = function (tag) {
  $(`.loadingImg${tag}`).remove();
  // $("#searchBtn").text("Search").prop("disabled", false);
};

const renderSearchLoading = function () {
  $(".searchBarIcon").attr("src", "/static/images/loading-icon.jpeg");
  // $(".veritasSearchInput").attr("disabled", "disabled"); this breaks query
  $(".veritasSearchBtn").attr("disabled", "disabled");
  $(".headlines").empty();
};

const deleteAccount = async function (e) {
  const $tgt = $(e.target);
  const userId = $tgt.data().uid;
  console.log(`User Id: ${userId}`);
  try {
    const res = await axios({
      url: `/users/${userId}/delete`,
      method: "DELETE",
    });
    console.log("Res: ");
    console.dir(res);
    location.href = "/";
  } catch (e) {
    alert(`Something went wrong during Query Deletion. Error info:${e}`);
  }
};

const deleteQuery = async function (e) {
  const $tgt = $(e.target);
  const dataId = $tgt.closest("span").data().qid;
  console.log(`Query Id: ${dataId}`);
  try {
    const res = await axios({
      url: `/queries/${dataId}`,
      method: "DELETE",
    });
    $tgt.closest("span").remove();
    console.log(`Query deleted!`);
  } catch (e) {
    alert(`Something went wrong during Query Deletion. Error info:${e}`);
  }
};

// const fetchAndShowContent = async function() {
// 	$('#articlesContainer').hide();
// 	showLoadingView($('#articlesHeader'), 'articles');
// 	$('#tweetsContainer').hide();
// 	showLoadingView($('#tweetsHeader'), 'tweets');
// 	// This should be a separate function:
// 	const articles = await getArticles(window.name);
// 	if (Boolean(articles)) {
// 		hideLoadingView('articles');
// 		displayArticles();
// 		$('#articlesContainer').show();
// 	} else {
// 		displayNoResults('articles');
// 		// hideLoadingView('articles');
// 		// alert('No articles found! Nothing to display.');
// 		// let msg = "We couldn't find any articles that were relevant. Try a different search?";
// 		// const $msgSpan = $(`<span>${msg}</span>`);
// 		// $('#articlesContainer').append($msgSpan);
// 		// $('#articlesContainer').show();
// 	}
// 	const tweets = await getEmbedTweets(window.name);
// 	if (Boolean(tweets)) {
// 		hideLoadingView('tweets');
// 		renderEmbedTweets();
// 		$('#tweetsContainer').show();
// 		await twttr.widgets.load();
// 	} else {
// 		// Handle case where no tweets are found
// 		displayNoResults('tweets');
// 		// hideLoadingView('tweets');
// 		// alert('No tweets found! Nothing to display.');
// 	}
// };

// const displayNoResults = function(targetEl) {
// 	hideLoadingView(targetEl);
// 	$(`#${targetEl}Container`).empty();
// 	// alert('No articles found! Nothing to display.');
// 	let msg = `We couldn't find any ${targetEl} that were relevant. Try a different search?`;
// 	const $msgSpan = $(`<span>${msg}</span>`);
// 	$(`#${targetEl}Container`).append($msgSpan).show();
// 	// $(`#${targetEl}Container`).show();
// };

// const asyncLocalStorage = {
// 	setItem: async function(key, value) {
// 		await null;
// 		return localStorage.setItem(key, value);
// 	},
// 	getItem: async function(key) {
// 		await null;
// 		return localStorage.getItem(key);
// 	}
// };

// const getArticles = async function(query) {
// 	try {
// 		const res = await axios({
// 			method: 'GET',
// 			url: '/api/articles',
// 			params: {
// 				q: query
// 			}
// 		});

// 		if (res.data.error) {
// 			console.log('No articles found!');
// 			return false;
// 		}
// 		asyncLocalStorage.setItem('articles', JSON.stringify(res.data));
// 		return res.data;
// 	} catch (e) {
// 		alert(`Internal API issue Fetching Articles. Error Info: ${e}`);
// 	}
// };

// const getEmbedTweets = async function(query) {
// 	try {
// 		const res = await axios({
// 			method: 'GET',
// 			url: '/api/tweets',
// 			params: {
// 				q: query
// 			}
// 		});
// 		if (res.data.error) {
// 			console.log('No tweets found!');
// 			return false;
// 		}
// 		asyncLocalStorage.setItem('tweets', JSON.stringify(res.data));
// 		return res.data;
// 	} catch (e) {
// 		alert(`Internal API issue Fetching Tweets. Error Info: ${e}`);
// 	}
// };

// const getTweets = async function(query) {
// 	try {
// 		const res = await axios({
// 			method: 'GET',
// 			url: '/api/tweets',
// 			params: {
// 				q: query
// 			}
// 		});
// 		if (res.data.error) {
// 			console.log('No tweets found!');
// 			return;
// 		}
// 		asyncLocalStorage.setItem('tweets', JSON.stringify(res.data));
// 		console.log('localStorage["tweets"] updated!');
// 		// return res.data;
// 	} catch (e) {
// 		alert(`Internal API issue Fetching Tweets. Error Info: ${e}`);
// 	}
// };

// const retrieveTwitterCard = async function(id, maxWidth = 220, omitScript = false, hideMedia = false) {
// 	try {
// 		const res = await axios({
// 			method: 'GET',
// 			url: 'https://publish.twitter.com/oembed',
// 			params: {
// 				url: `https://twitter.com/Interior/status/${id}`,
// 				maxwidth: maxWidth,
// 				hide_media: hideMedia,
// 				omit_script: omitScript
// 			}
// 		});
// 		console.dir(res);
// 		return res.data;
// 	} catch (e) {
// 		alert(`Issue fetching Twitter Cards. Error info: ${e}`);
// 	}
// };

// const renderEmbedTweets = function() {
// 	tweets = JSON.parse(localStorage.getItem('tweets')).tweets;
// 	const positive = tweets[0];
// 	const neutral = tweets[1];
// 	const negative = tweets[2];

// 	if (positive.length > 0) {
// 		for (let t of positive) {
// 			appendTweet(t, positiveTweetContainer);
// 		}
// 	}
// 	if (neutral.length > 0) {
// 		for (let t of neutral) {
// 			appendTweet(t, neutralTweetContainer);
// 		}
// 	}
// 	if (negative.length > 0) {
// 		for (let t of negative) {
// 			appendTweet(t, negativeTweetContainer);
// 		}
// 	}
// };

// // const renderTweets = function() {
// // 	tweets = JSON.parse(localStorage.getItem('tweets')).tweets;
// // 	const positive = tweets[0];
// // 	const neutral = tweets[1];
// // 	const negative = tweets[2];

// // 	if (positive.length > 0) {
// // 		for (let t of positive) {
// // 			appendTweet(t.id, positiveTweetContainer);
// // 		}
// // 	}
// // 	if (neutral.length > 0) {
// // 		for (let t of neutral) {
// // 			appendTweet(t.id, neutralTweetContainer);
// // 		}
// // 	}
// // 	if (negative.length > 0) {
// // 		for (let t of negative) {
// // 			appendTweet(t.id, negativeTweetContainer);
// // 		}
// // 	}
// // };

// const appendTweet = function(tweet, targetEl) {
// 	const container = document.createElement('div');
// 	const tweetCard = document.createElement('div');
// 	const sentDiv = document.createElement('div');
// 	const polarity = document.createElement('span');
// 	polarity.innerText = `Score: ${tweet.polarity}`;
// 	sentDiv.append(polarity);
// 	tweetCard.innerHTML = tweet.oembed_url;
// 	container.append(sentDiv, tweetCard);
// 	targetEl.append(container);
// };

// const appendTweetWidget = function(id, targetEl) {
// 	twttr.widgets.createTweet(id, targetEl, {
// 		cards: 'hidden'
// 	});
// };

// // const createAndAppendTweetHTML = function(tweet, targetEl) {
// // 	const container = document.createElement('div');
// // 	const tweetCard = document.createElement('div');
// // 	const sentDiv = document.createElement('div');
// // 	const polarity = document.createElement('span');
// // 	polarity.innerText = `Score: ${tweet.polarity}`;
// // 	sentDiv.append(polarity);
// // 	tweetCard.innerHTML = tweet.oembed_url;
// // 	container.append(sentDiv, tweetCard);
// // 	targetEl.append(container);
// // }

// const displayArticles = function() {
// 	articles = JSON.parse(localStorage.getItem('articles')).articles;
// 	const positive = articles[0];
// 	const neutral = articles[1];
// 	const negative = articles[2];

// 	if (positive.length > 0) {
// 		for (let a of positive) {
// 			appendArticle(a, 'positive');
// 		}
// 	}
// 	if (neutral.length > 0) {
// 		// append all neutral articles
// 		for (let a of neutral) {
// 			appendArticle(a, 'neutral');
// 		}
// 	}
// 	if (negative.length > 0) {
// 		// append all negative articles
// 		for (let a of negative) {
// 			appendArticle(a, 'negative');
// 		}
// 	}
// };

// const appendArticle = function(article, sentKey) {
// 	let targetTag;
// 	const sentKeys = {
// 		positive: 'Positive',
// 		neutral: 'Neutral',
// 		negative: 'Negative'
// 	};

// 	if (sentKey.length > 0) {
// 		targetTag = `articles${sentKeys[sentKey]}`;
// 	}

// 	const newArticle = $(`
//     <div class="border border-black p-1 text-sm">
//       <h2 class="font-semibold">${article.title}</h2>
//       <p>${article.description}</p>
//       <p class="text-xs font-medium">Polarity: ${article.polarity}</p>
//       <div class="text-xs">
//         <span>By ${article.source}</span>
//         <span> on ${article.published}</span>
//       </div>
//     </div>
//   `);

// 	$(`#${targetTag}`).append(newArticle);
// };
