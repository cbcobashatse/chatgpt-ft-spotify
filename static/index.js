{/* <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script> */}

$(document).ready(function() {
    // Attach event listener to form submission
//     $("#submit-button").click(function(event){
//         // event.preventDefault();
//         console.log("hello")
//     })
// })

    // var button = document.getElementById("submit-button");
    // button.addEventListener("click", function(event) {
    //     // handle form submission here
    //     console.log("hello")
    // });

    $('form').submit(function(event) {
        // Prevent default form submission behavior
        event.preventDefault();
        $('#result-container').empty();
        console.log(event)
        // Make AJAX POST request to /get-spotify-url
        const songInput = document.getElementById("song-input");
        const songText = songInput.value;
        console.log(songText)
        let data = {"content": songText}
        console.log(data)
        $.ajax({
            type: 'POST',
            url: '/get-spotify-url',
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            success: function(response) {
                // Display the results in the result container
                console.log(response['track_urls'])
                tracks = response['track_urls']

                var resultHtml = '';
                $.each(tracks, function(index, value) {
                  var songName = value[0];
                  var spotifyUrl = value[1];
                  var embedUrl = spotifyUrl.replace('/track/', '/embed/track/');
                  resultHtml += (index + 1) + '. ' + songName + '<br><iframe src="' + embedUrl + '" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe><br>';
                });
                console.log(resultHtml)
                $('#result-container').html(resultHtml);
            },
            error: function(xhr, status, error) {
                console.log(error);
                var error_msg = "There was an error in the processing of your request!<br>"
                + "Use the format 'Give me N random songs with a X [measure]'<br><br>"
                + "Currently, the app supports Beats Per Minute (BPM) and danceability.<br>"
                + "Danceability can be between 0.0 and 1.0!<br>"
                + "BPM varies between 60 and 200 for most songs!"
                $('#result-container').html(error_msg);
            }
        });
    });
});
