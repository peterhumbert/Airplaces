function getExif() {
    var imgTag = $('#img2')[0];
    var airline = "UAL"; // TODO
    var flightno = "21"; // TODO
    imgTag.exifdata = null; // needed to prevent caching of exif data

    EXIF.getData(imgTag, function() {
        var latref = EXIF.getTag(this, "GPSLatitudeRef");
        var lat = EXIF.getTag(this, "GPSLatitude");
        var lonref = EXIF.getTag(this, "GPSLongitudeRef");
        var lon = EXIF.getTag(this, "GPSLongitude");
        var datetime = EXIF.getTag(this, "DateTime");
        var allMetaDataSpan = $('#allMetaDataSpan')[0];

        var datetimeFormatted = datetime.substring(0,4) + datetime.substring(5,7)
          + datetime.substring(8,10) + datetime.substring(11,13)
          + datetime.substring(14,16) + datetime.substring(17,19);

        // AJAX call
        $.ajax({url: "http://localhost:4000/"+ airline + "/" + flightno + "/" +
          datetimeFormatted, success: function(result){
            console.log($("#allMetaDataSpan"));
            $("#allMetaDataSpan")[0].innerHTML = result;
        }});
    });
}


function readURL(input) {
  console.log('readURL');
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
        $('#img2').attr('src', e.target.result);
    };

    reader.readAsDataURL(input.files[0]);
    /*
    var img2 = document.getElementById("img2");
    EXIF.getData(img2, function() {
        var make = EXIF.getTag(this, "Make");
        var model = EXIF.getTag(this, "Model");
        var makeAndModel = document.getElementById("allMetaDataSpan");
        makeAndModel.innerHTML = `${make} ${model}`;
    });
    */
  }
}

function loadSampleImage() {
  console.log('load sample image');
  $('#img2')[0].setAttribute('src','IMAG2105.jpg');
}

$(document).ready(function() {
  // make the image only as tall as the map
  $('#img2').attr('style',$('#img2').attr('style') + 'max-height:' + $('#map')[0].clientHeight + 'px;');

  // setup the airline dropdown
  $('#airlines').dropdown();
})
