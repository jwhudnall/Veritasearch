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
  // Runs on personal results page only
  if ($("#personalizedResultContainer").length > 0) {
    $("#personalizedResultContainer").hide();
    $(".searchForTruthBlock").hide();
  }
  // Personalized User Content Action
  $("#getUserContent").on("click", async function () {
    updateBtnAndSearchContainer("#getUserContent");
    await fetchAndShowRecommendations("#queryContainer", "#getUserContent");
  });
  $("#getDemoUserContent").on("click", handleDemoResults);
  $(".veritasSearchForm").on("submit", renderSearchLoading);
  $("#queryContainer").on("click", "button", deleteQuery);
  $("#queryContainerDemo").on("click", "button", deleteQueryDemo);
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

const handleDemoResults = async function () {
  if ($("#queryContainerDemo").children().length > 0) {
    updateBtnAndSearchContainer("#getDemoUserContent");
    await fetchAndShowRecommendations(
      "#queryContainerDemo",
      "#getDemoUserContent"
    );
  } else {
    $refresh = $(
      '<span class="text-blue-400"><a href="/users/demo">Click to refresh page.</a></span>'
    );
    $("#userRecMsg")
      .text("Past search history is needed to provide recommendations. ")
      .append($refresh);
    $("#getDemoUserContent").hide();
  }
};

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
  $("#convertingMsg").hide();
  setTimeout(function () {
    renderEmbedTweets(tweetsPositive, tweetsNeutral, tweetsNegative);
  }, 500);
  $divs.hide();
  showLoadingView($divs, "tweetDivs");
  $(".actSignupCTA").hide();
  setTimeout(function () {
    // Post rendering actions
    $divs.show();
    hideLoadingView("tweetDivs");
    $(".actSignupCTA").show();
    $("#convertingMsg").addClass("fade-in-block").show();
    $("#searchResultsUsrMsg").text("Here's what we found:");
  }, 3000);
};

const fetchAndShowRecommendations = async function (target, btn) {
  emptyTweetContainers();
  const query = selectQueriesForSearch(target);
  const $divs = $(".fade-in-div");
  $divs.hide();
  showLoadingView($divs, "tweetDivs");
  // Query API for recommended tweets
  const res = await getTweetRecommendations(query);
  setTimeout(function () {
    $(btn).text("Complete");
    $(btn).fadeTo(5000, 0);
    $("#userRecMsg").text(
      "Your recommendations change over time, and improve as you make more searches."
    );
    $divs.show();
    hideLoadingView("tweetDivs");
    $(".searchForTruthBlock").show();
  }, 3000);

  try {
    if (res.error !== undefined) {
      return false;
    }
    if (res.tweets !== undefined) {
      const recTweets = res.tweets;
      renderEmbedTweets(recTweets[0], recTweets[1], recTweets[2]);
    }
  } catch (e) {
    alert("Something went wrong. Please try again.");
  }
};

const getTweetRecommendations = async function (query) {
  try {
    const res = await axios.get("/api/tweets", { params: { query } });
    return res.data;
  } catch (e) {
    alert(
      `Something went wrong during Personalized Tweet Recommendation Search. Please try again later.Error info:${e}`
    );
  }
};

const updateBtnAndSearchContainer = function (btn) {
  $("#personalizedResultContainer").show();
  $(btn).prop("disabled", true);
  $(btn).text("Searching...");
};

const selectQueriesForSearch = function (target) {
  // Sends all queries to the backend for processing
  if ($(target).length > 0) {
    let s = "";
    const queries = $(target).find("span");
    for (let q of queries) {
      let cur = q.innerText.trim();
      s += cur + ",";
    }
    let queryString = s.substring(0, s.length - 1); // Remove trailing comma
    return queryString;
  } else {
    return False;
  }
};

const getLoginFormHTML = async function () {
  const res = await axios({
    url: "/login",
    method: "PUT",
  });
  return res.data;
};

const getRegisterFormHTML = async function () {
  const res = await axios({
    url: "/register",
    method: "PUT",
  });
  return res.data;
};

const showLoadingView = function ($targetEl, tag) {
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
};

const renderSearchLoading = function () {
  $(".searchBarIcon").attr("src", "/static/images/loading-icon.jpeg");
  $(".veritasSearchBtn").attr("disabled", "disabled");
  $(".headlines").empty();
};

const deleteAccount = async function (e) {
  const $tgt = $(e.target);
  const userId = $tgt.data().uid;
  try {
    const res = await axios({
      url: `/users/${userId}`,
      method: "DELETE",
    });
    location.href = "/";
  } catch (e) {
    alert(`Something went wrong during Account Deletion. Error info:${e}`);
  }
};

const deleteQuery = async function (e) {
  const $tgt = $(e.target);
  const dataId = $tgt.closest("div").data().qid;
  $tgt.closest("div").remove();
  await deleteQueryFromDB(dataId);
};

const deleteQueryFromDB = async function (dataId) {
  try {
    const res = await axios({
      url: `/queries/${dataId}`,
      method: "DELETE",
    });
  } catch (e) {
    alert(`Something went wrong during Query Deletion. Error info:${e}`);
  }
};

const deleteQueryDemo = function (e) {
  const $tgt = $(e.target);
  $tgt.closest("div").remove();
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
    `to-${divColor}-500`,
    "fade-in-block"
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

function searchText(speed, txt) {
  let i = 0;
  function typeWriter() {
    if (i < txt.length) {
      document.getElementsByClassName("veritasSearchInput")[0].value +=
        txt.charAt(i);
      i++;
      setTimeout(typeWriter, speed);
    }
  }
  typeWriter();
}
