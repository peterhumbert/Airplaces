function getExif() {
    var imgTag = $('#img2')[0];
    imgTag.exifdata = null; // needed to prevent caching of exif data
    EXIF.getData(imgTag, function() {
        var allMetaData = EXIF.getAllTags(this);
        var allMetaDataSpan = document.getElementById("allMetaDataSpan");
        console.log(allMetaData);
        allMetaDataSpan.innerHTML = JSON.stringify(allMetaData, null, "\t");
    });
}


function readURL(input) {
  console.log('readURL');
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
        $('#img2')
            .attr('src', e.target.result)
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
