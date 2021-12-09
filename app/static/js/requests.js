$(document).ready(function () {
	if (!$.curCSS) $.curCSS = $.css;

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
					// Autocomplete suggestions for usernames
					var usernames = []
					response.forEach(function (user) {
						suggestion = user['username']
						usernames.push(suggestion);
						$('#friend_suggestions').append('<li><a class="btn btn-secondary" href="#">' + suggestion + '</a></li>')
					});
				},
				error: function (error) {
					console.log("Error " + error);
				}
			});
		}
	});
});