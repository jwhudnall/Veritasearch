const positiveTweetContainer = document.getElementById(
  "tweetsPositiveContainer"
);
const neutralTweetContainer = document.getElementById("tweetsNeutralContainer");
const negativeTweetContainer = document.getElementById(
  "tweetsNegativeContainer"
);

$(document).ready(async function () {
  if ($("#searchResultContainer").length > 0) {
    const $divs = $(".fade-in-div");
    setTimeout(renderEmbedTweets, 500);
    $divs.hide();
    showLoadingView($divs, "tweetDivs");
    setTimeout(function () {
      $divs.show();
      hideLoadingView("tweetDivs");
      $(".actSignupCTA").show();
    }, 3000);

    // Account Signup CTA
    $(".actSignupCTA").hide();
  }

  $(".veritasSearchForm").on("submit", renderSearchLoading);

  $("#queryContainer").on("click", "button", deleteQuery);
  $("#delActBtn").on("click", deleteAccount);

  $("#headlineWords").on(
    "click",
    ".veritasSearchSuggestion",
    renderSearchLoading
  );
  // User Registration Action
  $("body").on("click", ".registrationModalBtn", async function () {
    const html = await getRegisterFormHTML();
    $("#userRegisterSection").append(html);
  });
  $("body").on("click", "#registerUserModalClose", function () {
    $("#userRegisterSection").empty();
    toggleModal("registration-modal", false);
  });

  // User Login Action
  $("body").on("click", ".loginModalBtn", async function () {
    const html = await getLoginFormHTML();
    $("#userLoginSection").append(html);
  });
  $("body").on("click", "#loginUserModalClose", function () {
    $("#userLoginSection").empty();
    toggleModal("login-modal", false);
  });
});

const getLoginFormHTML = async function () {
  const res = await axios({
    url: "/login/returningUser",
    method: "GET",
  });
  return res.data;
};

const getRegisterFormHTML = async function () {
  const res = await axios({
    url: "/register/newUserSignup",
    method: "GET",
  });
  return res.data;
};

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
  const dataId = $tgt.closest("div").data().qid;
  console.log(`Query Id: ${dataId}`);
  try {
    const res = await axios({
      url: `/queries/${dataId}`,
      method: "DELETE",
    });
    $tgt.closest("div").remove();
    console.log(`Query deleted!`);
  } catch (e) {
    alert(`Something went wrong during Query Deletion. Error info:${e}`);
  }
};

const selectQueriesForSearch = function () {
  // Currently returns a random query for search
  if ($("#queryContainer").length > 0) {
    let queries = $("#queryContainer").find("span");
    let randIdx = Math.floor(Math.random() * queries.length);
    let choice = queries[randIdx].innerText.trim();
    return choice;
  } else {
    return False;
  }
};

const fetchAndShowContent = async function () {
  // Main page loading sequence here
};

const renderEmbedTweets = function () {
  if (tweetsPositive.length > 0) {
    for (let t of tweetsPositive) {
      createAndAppendTweetWidget(t, positiveTweetContainer, "lime");
    }
  }
  if (tweetsNeutral.length > 0) {
    for (let t of tweetsNeutral) {
      createAndAppendTweetWidget(t, neutralTweetContainer, "amber");
    }
  }
  if (tweetsNegative.length > 0) {
    for (let t of tweetsNegative) {
      createAndAppendTweetWidget(t, negativeTweetContainer, "red");
    }
  }
};

const createAndAppendTweetWidget = function (tweet, targetContainer, divColor) {
  const sentimentContainer = document.createElement("div");
  sentimentContainer.classList.add("relative", "w-48", "mx-auto");

  const sentDiv = document.createElement("div");
  sentDiv.classList.add(
    "absolute",
    "top-0",
    "right-0",
    "border",
    "border-1",
    "text-center",
    "px-1",
    "bg-gradient-to-r",
    `from-${divColor}-100`,
    `to-${divColor}-500`
  );

  const resultSpan = document.createElement("span");
  resultSpan.classList.add("font-semibold", "text-base", "dark:text-black");

  const sentSpan = document.createElement("span");
  sentSpan.classList.add("font-semibold");
  sentSpan.innerText = `${tweet.sentiment}`;

  const scoreSpan = document.createElement("span");
  scoreSpan.classList.add("italic", "text-xs");
  scoreSpan.innerText = ` (Polarity: ${tweet.polarity})`;

  resultSpan.append(sentSpan, scoreSpan);
  sentDiv.append(resultSpan);
  sentimentContainer.append(sentDiv);

  const tweetDiv = document.createElement("div");
  tweetDiv.classList.add("flex", "justify-center");
  twttr.widgets.createTweet(tweet.id, tweetDiv, {
    cards: "hidden",
  });

  targetContainer.append(sentimentContainer, tweetDiv);
};

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
