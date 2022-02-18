const positiveTweetContainer = document.getElementById(
  "tweetsPositiveContainer"
);
const neutralTweetContainer = document.getElementById("tweetsNeutralContainer");
const negativeTweetContainer = document.getElementById(
  "tweetsNegativeContainer"
);

$(document).ready(async function () {
  $(".flashMessage").delay(2000).slideUp();
  if ($("#searchResultContainer").length > 0) {
    fetchAndShowContent();
  }

  if ($("#personalizedResultContainer").length > 0) {
    console.log("Personal result container located!");
    $("#personalizedResultContainer").hide();
    $(".searchForTruthBlock").hide();
  }

  // Personalized User Content Action
  $("#getUserContent").on("click", async function () {
    console.log("Recommendations btn clicked!");
    $("#personalizedResultContainer").show();
    $("#getUserContent").prop("disabled", true);
    $("#getUserContent").text("Searching...");
    await fetchAndShowRecommendations();
    // $("#getUserContent").text("Done!");
    // $("#getUserContent").hide();
    // $(".searchForTruthBlock").show();
  });

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
const emptyTweetContainers = function () {
  const containers = [
    positiveTweetContainer,
    neutralTweetContainer,
    negativeTweetContainer,
  ];
  containers.forEach((c) => {
    c.innerHTML = "";
  });
};

const fetchAndShowContent = async function () {
  const $divs = $(".fade-in-div");
  setTimeout(function () {
    renderEmbedTweets(tweetsPositive, tweetsNeutral, tweetsNegative);
  }, 500);
  $divs.hide();
  showLoadingView($divs, "tweetDivs");
  setTimeout(function () {
    $divs.show();
    hideLoadingView("tweetDivs");
    $(".actSignupCTA").show();
  }, 3000);
  // Account Signup CTA
  $(".actSignupCTA").hide();
};

const fetchAndShowRecommendations = async function () {
  emptyTweetContainers();
  const query = selectQueriesForSearch();
  const $divs = $(".fade-in-div");
  $divs.hide();
  showLoadingView($divs, "tweetDivs");
  const res = await getTweetRecommendations(query);
  setTimeout(function () {
    $("#getUserContent").text("Done!");
    $divs.show();
    hideLoadingView("tweetDivs");
    $(".searchForTruthBlock").show();
  }, 3000);

  if (res.error !== undefined) {
    // Handle case with no results. Query another?
    console.log("No Tweets found.");
    return false;
  }
  if (res.tweets !== undefined) {
    const recTweets = res.tweets;
    console.log("Rendering Tweets...");
    renderEmbedTweets(recTweets[0], recTweets[1], recTweets[2]);
    console.log("Finished rendering!");
  }
};

const getTweetRecommendations = async function (query) {
  try {
    const res = await axios.get("/api/tweets", { params: { query } });
    return res.data;
  } catch (e) {
    alert(
      `Something went wrong during Personalized Tweet Recommendation Search. Error info:${e}`
    );
  }
};

const selectQueriesForSearch = function () {
  // Currently returns a random query for search
  if ($("#queryContainer").length > 0) {
    let s = "";
    const queries = $("#queryContainer").find("span");
    for (let q of queries) {
      let cur = q.innerText.trim();
      s += cur + ",";
    }
    let queryString = s.substring(0, s.length - 1); // Remove trailing comma
    return queryString;
    // let randIdx = Math.floor(Math.random() * queries.length);
    // let choice = queries[randIdx].innerText.trim();
    // return choice;
  } else {
    return False;
  }
};

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
  const $loadingDiv = $("<div>")
    .addClass("h-96 flex flex-col justify-center")
    .addClass(`loadingImg${tag}`);
  const $loadingIcon = $("<img>")
    .attr({
      src: "/static/images/loading-icon.jpeg",
    })
    .addClass("w-32 mx-auto mt-5");
  $loadingDiv.append($loadingIcon);
  $loadingDiv.insertAfter($targetEl);
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
      url: `/users/${userId}`,
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

const renderEmbedTweets = function (positive, neutral, negative) {
  if (positive.length > 0) {
    for (let t of positive) {
      createAndAppendTweetWidget(t, positiveTweetContainer, "lime");
    }
  } else {
    createAndAppendNoResults(positiveTweetContainer);
  }
  if (neutral.length > 0) {
    for (let t of neutral) {
      createAndAppendTweetWidget(t, neutralTweetContainer, "amber");
    }
  } else {
    createAndAppendNoResults(neutralTweetContainer);
  }
  if (negative.length > 0) {
    for (let t of negative) {
      createAndAppendTweetWidget(t, negativeTweetContainer, "red");
    }
  } else {
    createAndAppendNoResults(negativeTweetContainer);
  }
};

const createAndAppendNoResults = function (target) {
  const msg = document.createElement("p");
  msg.classList.add("text-center");
  msg.innerText = "No results found for this category.";
  target.append(msg);
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
