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

    // Initially hide search_friend button
    $("#search_friend").removeClass("d-none").hide();
    $("#search_friend_cancel").removeClass("d-none").hide();
    // Swap add friend for search box
    $("#add_friend").click(function () {
        $(this).hide();
        $("#search_friend").show();
        $("#search_friend_cancel").show();
    });
    // Cancel friend search
    $("#search_friend_cancel").click(function () {
        $("#search_friend_cancel").hide();
        $("#search_friend").hide();
        $("#add_friend").show();
        $("#search_friend").val("");
        $('#friend_suggestions').empty();
    });
});