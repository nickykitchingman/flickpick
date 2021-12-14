$(document).ready(function () {
	if (!$.curCSS) $.curCSS = $.css;

	var friendSuggestions = []
	var currentMovieId = -1;

	// Set CSRF token to start of every request
	var csrf_token = $('meta[name=csrf-token]').attr('content')
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrf_token);
			}
		}
	});

	// Start searching for users
	$("#search_friend").on('input', function () {
		var username = $(this).val();

		if (username == "") {
			$("#friend_suggestions").empty();
			friendSuggestions.length = 0;
		}
		else {
			$.ajax({
				url: '/users_like',
				type: 'POST',
				data: JSON.stringify({ username: username }),
				contentType: "application/json; charset=utf-8",
				datatype: "json",

				success: function (response) {
					var username = $("#search_friend").val();
					if (username != "") {
						// Autocomplete suggestions for usernames
						$('#friend_suggestions').empty();
						friendSuggestions.length = 0;
						var i = 0;
						response.forEach(function (user) {
							suggestion = user['username']
							friendSuggestions.push(user);
							$('#friend_suggestions').append('<li><a id="suggestion' + i +
								'" class="suggestion btn btn-secondary">' + suggestion + '</a></li>');
							i++;
						});
					}
				},
				error: function (error) {
					console.log("Error " + error.responseText);
				}
			});
		}
	});

	// Send friend request
	$(document).on('click', '.suggestion', function () {
		var friendId = parseInt($(this).attr('id').replace('suggestion', ''));
		var user = friendSuggestions[friendId];

		$.ajax({
			url: '/friend_request',
			type: 'POST',
			data: JSON.stringify({ userId: user.userId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',

			success: function (response) {
				$('#suggestion' + friendId).hide();
			},
			error: function (error) {
				console.log('Error: ' + error.responseText);
			}
		});
	});

	// Accept friend request
	$('.accept').click(function () {
		userId = $(this).parent().attr('id').replace('request', '');

		$.ajax({
			url: '/request_accept',
			type: 'POST',
			data: JSON.stringify({ userId: userId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',

			success: function (response) {
				$('#request' + userId).hide();
			},
			error: function (error) {
				console.log('Error: ' + error.responseText);
			}
		});
	});

	// Decline friend request
	$('.decline').click(function () {
		userId = $(this).parent().attr('id').replace('request', '');

		$.ajax({
			url: '/request_decline',
			type: 'POST',
			data: JSON.stringify({ userId: userId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',

			success: function (response) {
				$('#request' + userId).hide();
			},
			error: function (error) {
				console.log('Error: ' + error.responseText);
			}
		});
	});

	// Set next movie in movie picker
	function nextMovie(funcAfter = null) {
		$.get("/next_movie", function (response) {
			if (response.movie == null) {
				finishPicker();
				return;
			}

			// Set first movie in picker
			$("#movie-name").text(response.movie.name);
			$("#movie-date").text(response.movie.releasedate);
			currentMovieId = response.movie.movieId;

			// Enable buttons
			$("#yes").removeClass("disabled");
			$("#maybe").removeClass("disabled");
			$("#no").removeClass("disabled");

			// Optionally return to other func
			if (funcAfter != null)
				funcAfter();
		});
	}

	function swapToPicker() {
		// Enable buttons
		$("#yes").removeClass("disabled");
		$("#maybe").removeClass("disabled");
		$("#no").removeClass("disabled");

		$("#movie-picker-btn").hide();
		$("#movie-picker").show();
	}

	function finishPicker() {
		$("#movie-picker").hide();
		$("#movie-picker-btn").show();
	}

	// Initially hide movie picker
	$("#movie-picker").hide().removeClass("d-none");
	// Swap movie picker button for movie picker
	$("#movie-picker-btn").click(function () {
		// Disable buttons
		$("#yes").addClass("disabled");
		$("#maybe").addClass("disabled");
		$("#no").addClass("disabled");

		// Clear movie choices and swap
		$.get("/clear_movies");
		nextMovie(swapToPicker);
	});

	// Make decision on movie
	$(".decision").click(function () {
		var strDecision = $(this).attr("id");
		var decision = -1;

		// Decision to number for ease
		switch (strDecision) {
			case "yes": decision = "2"; break;
			case "maybe": decision = "1"; break;
			case "no": decision = "0"; break;
		}

		// Disable buttons
		$("#yes").addClass("disabled");
		$("#maybe").addClass("disabled");
		$("#no").addClass("disabled");

		// Send decision to server
		if (decision != -1 && currentMovieId != -1) {
			$.ajax({
				url: '/add_movie',
				type: 'POST',
				data: JSON.stringify({ movieId: currentMovieId, decision: decision }),
				contentType: 'application/json; charset=utf-8',
				datatype: 'json',

				// Change movie picker
				success: function (response) {
					nextMovie();
				},
				error: function (error) {
					console.log('Error: ' + error.responseText);
				}
			});
		}
		// Invalid decision
		else if (decision != -1)
			console.log("Error - Invalid 'decision' class clicked");
		else
			console.log("Error - Invalid current movie id");
	});

	function decToHex(rgb) {
		var hex = parseInt(rgb).toString(16);
		if (hex.length < 2) {
			hex = "0" + hex;
		}
		return hex;
	}

	// Show matches with friend or group, 
	// assigning each a colour based on strength of match
	function showMatches(response) {
		$("#matches").empty();
		var val = 2 * 255 / response.maxStrength;

		response.matches.forEach(function (match) {
			console.log(match.strength);
			var thisVal = match.strength * val;
			var R = decToHex(255 - Math.max(thisVal - 255, 0));
			var G = decToHex(Math.min(thisVal, 255));
			var B = decToHex(0);
			var percentMatch = parseInt(match.strength / response.maxStrength * 100);
			$("#matches").append(
				`<li class="list-group-item" 
						style="background-color:#${R}${G}${B};"><h2>
						${match.name}</h2><p>
						${match.releasedate}</p><div class="float-right font-weight-bold">
						${percentMatch}%</div></li>`
			);
		});
	}

	// Match movies with friend
	$(".friend").click(function () {
		var friendId = $(this).attr("id").replace("friend", "");

		$.ajax({
			url: '/match_friend',
			type: 'POST',
			data: JSON.stringify({ friendId: friendId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',

			// Change movie picker
			success: function (response) {
				showMatches(response);
			},
			error: function (error) {
				console.log('Error: ' + error.responseText);
			}
		});
	});

	// Match movies with group
	$(".group").click(function () {
		var groupId = $(this).attr("id").replace("group", "");

		$.ajax({
			url: '/match_group',
			type: 'POST',
			data: JSON.stringify({ groupId: groupId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',

			// Change movie picker
			success: function (response) {
				console.log(`max: ${response.maxStrength}`);
				showMatches(response);
			},
			error: function (error) {
				console.log('Error: ' + error.responseText);
			}
		});
	});

	// Submit create group
	$("#create_submit").click(function () {
		var name = $("#name_group").val();

		if (name != "") {
			$.ajax({
				url: '/create_group',
				type: 'POST',
				data: JSON.stringify({ name: name }),
				contentType: "application/json; charset=utf-8",
				datatype: "json",

				success: function (response) {
					$("#create_group_error").text("");
					error = response.error

					// Display error if exists
					if (error)
						$("#create_group_error").text(error);
					else
						window.location.reload();
				},
				error: function (error) {
					console.log("Error " + error.responseText);
				}
			});
		}
	});

	// Delete group
	$(".leave").click(function () {
		var panel = $(this).closest("[id^=group]");
		var groupId = panel.attr(("id")).replace("group", "");

		// Disable buttons
		panel.addClass("disabled");
		$(this).addClass("disabled");
		panel.find(".edit").addClass("disabled");
		panel.find(".invite").addClass("disabled");

		$.ajax({
			url: '/leave_group',
			type: 'POST',
			data: JSON.stringify({ groupId: groupId }),
			contentType: "application/json; charset=utf-8",
			datatype: "json",

			success: function (response) {
				window.location.reload();
			},
			error: function (error) {
				console.log("Error " + error.responseText);
				panel.removeClass("disabled");
				$(this).removeClass("disabled");
				panel.find(".edit").removeClass("disabled");
				panel.find(".invite").removeClass("disabled");
			}
		});
	});
});