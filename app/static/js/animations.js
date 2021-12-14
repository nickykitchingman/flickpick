$(document).ready(function () {

    $(".friend").find(".hiddenpanel").removeClass("d-none").hide();

    // Show match option
    $(".friend").mouseenter(function () {
        $(this).find(".hiddenpanel").show();
    });
    // Hide match option
    $(".friend").mouseleave(function () {
        $(this).find(".hiddenpanel").hide();
    });

    // Initially hide search boxes
    $("#search_friend_container").hide().removeClass("d-none");
    $("#input_container").hide().removeClass("d-none");
    // Swap add friend for search box
    $("#add_friend").click(function () {
        $(this).hide();
        $("#search_friend_container").show();
    });
    // Cancel friend search
    $("#search_friend_cancel").click(function () {
        $("#search_friend_container").hide();
        $("#add_friend").show();
        $("#search_friend").val("");
        $('#friend_suggestions').empty();
    });

    // Disable input box submit when input is null
    $("#input_box").on("input", function () {
        var input = $("#input_box").val();

        if (input == "") {
            $("#input_submit").addClass("disabled");
        } else
            $("#input_submit").removeClass("disabled");
    });

    // Group actions appear on hover
    $(".group").on("mouseenter", function () {
        $(this).find(".hover").removeClass("d-none");
    });

    // Group actions appear on hover
    $(".group").on("mouseleave", function () {
        $(this).find(".hover").addClass("d-none");
    });
});