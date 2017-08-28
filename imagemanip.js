function getExif() {
    var imgTag = $('#img2')[0];
    imgTag.exifdata = null; // needed to prevent caching of exif data

    EXIF.getData(imgTag, function() {
        var latref = EXIF.getTag(this, "GPSLatitudeRef");
        var lat = EXIF.getTag(this, "GPSLatitude");
        var lonref = EXIF.getTag(this, "GPSLongitudeRef");
        var lon = EXIF.getTag(this, "GPSLongitude");
        var datetime = EXIF.getTag(this, "DateTime");
        var allMetaDataSpan = $('#allMetaDataSpan')[0];
        if (lat && lon) {
          console.log('What about airplane mode?');
          allMetaDataSpan.innerHTML = `${lat} ${latref} ${lon} ${lonref} \n${datetime}`;
          window.alert('What about airplane mode?');
        } else {
          console.log(datetime);
          allMetaDataSpan.innerHTML = `${datetime}`;
        }
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

$(document).ready(function() {
  // make the image only as tall as the map
  $('#img2').attr('style',$('#img2').attr('style') + 'max-height:' + $('#map')[0].clientHeight + 'px;');
})
