$(document).ready(function () {
	if (!$.curCSS) $.curCSS = $.css;

	var friend_suggestions = []

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
		}
		else {
			$.ajax({
				url: '/users_like',
				type: 'POST',
				data: JSON.stringify({ username: username }),
				contentType: "application/json; charset=utf-8",
				datatype: "json",
				success: function (response) {
					$('#friend_suggestions').empty();
					friend_suggestions.length = 0;
					// Autocomplete suggestions for usernames
					var i = 0;
					response.forEach(function (user) {
						suggestion = user['username']
						friend_suggestions.push(user);
						$('#friend_suggestions').append('<li><a id="suggestion' + i + 
							'" class="suggestion btn btn-secondary">' + suggestion + '</a></li>')
						i++;
					});
				},
				error: function (error) {
					console.log("Error " + error);
				}
			});
		}
	});

	// Send friend request
	$(document).on('click', '.suggestion', function() {
		console.log("click");
		var friendId = 	parseInt($(this).attr('id').replace('suggestion',''));
		console.log(friendId);
		var user = friend_suggestions[friendId];

		$.ajax({
			url: '/friend_request',
			type: 'POST',
			data: JSON.stringify({ userId: user.userId }),
			contentType: 'application/json; charset=utf-8',
			datatype: 'json',
			success: function(response) {
				console.log("Success.");
				$(this).hide();
			},
			error: function(error) {
				console.log('Error: ' + error);
			}
		});
	});
});