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
    $("#name_group_container").hide().removeClass("d-none");
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
    // Swap create group for name box
    $("#create_group").click(function () {
        $(this).hide();
        $("#name_group_container").show();
    });
    // Cancel name group
    $("#create_group_cancel").click(function () {
        $("#name_group_container").hide();
        $("#create_group").show();
        $("#name_group").val("");
    });

    // Disable create group submit when name is null
    $("#name_group").on("input", function () {
        var name = $("#name_group").val();

        if (name == "") {
            $("#create_submit").addClass("disabled");
        } else
            $("#create_submit").removeClass("disabled");
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