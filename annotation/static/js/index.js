var imgActualWidth = 0;
var imgActualHeight = 0;
var imgDisplayWidth = 900;
var imgDisplayHeight = 1200;
window.onload = function () {
  canvas = document.getElementById("canvas");
  ctx = canvas.getContext("2d");
  ctx.font = "30px Arial";
  ctx.fillStyle = "#FF0000";
  prev = document.getElementById("pdf-prev");
  next = document.getElementById("pdf-next");
  rect = {};
  drag = false;

  imageObj = null;
  coordinates = new Map();
  annotations = new Map();
  pageDimensions = new Map();
  id = 0;
  var _CURRENT_PAGE = 1;

  function init() {
    canvas.addEventListener("mousedown", mouseDown, false);
    canvas.addEventListener("mouseup", mouseUp, false);
    canvas.addEventListener("mousemove", mouseMove, false);
    prev.addEventListener("click", getprev, false);
    next.addEventListener("click", getnex, false);
    _CURRENT_PAGE = 1;
    $.getJSON("/media/currentcoors.json", function (json) {
      uploadedcoors = json;
      for (const [key, value] of Object.entries(uploadedcoors)) {
        ind = 0;
        if (key !== "ncols") {
          tempmap = new Map();
          for (let ele of value) {
            if(ele["IMAGE_ACTUAL_WIDTH"]!==undefined || ele["IMAGE_ACTUAL_HEIGHT"] !== undefined)continue;
            tempmap.set(ind.toString(), [
              ele["left"],
              ele["top"],
              ele["width"],
              ele["height"],
              ele["label"],
            ]);
            ind++;
          }
          annotations[key] = tempmap;
        }
      }
    });
    showPage(1);
  }

  function mouseDown(e) {
    rect.startX = e.pageX - this.offsetLeft;
    rect.startY = e.pageY - this.offsetTop;
    drag = true;
  }

  function mouseUp() {
    drag = false;
    var annotation_table_body = document.getElementById(
      "annotation_table_body"
    );
    console.log("Actual", rect.startX, rect.startY, rect.w, rect.h);
    console.log("Actual dims", imgActualWidth, imgActualHeight);
    console.log("Display dims", imgDisplayWidth, imgDisplayHeight);
    var startX = Math.floor((rect.startX * imgActualWidth) / imgDisplayWidth);
    var startY = Math.floor((rect.startY * imgActualHeight) / imgDisplayHeight);
    var w = Math.floor((rect.w * imgActualWidth) / imgDisplayWidth);
    var h = Math.floor((rect.h * imgActualHeight) / imgDisplayHeight);

    console.log("Scaled", startX, startY, w, h);

    $("#annotation_table_body").append(
      "<tr id='" +
        id +
        "' onclick='ShowRect(" +
        id +
        ");'>\
                    <td><input type='text' class='form-control' readonly name='startX' form='coordinate_form' value='" +
        startX +
        "'></td>\
                    <td><input type='text' class='form-control' readonly name='startY' form='coordinate_form' value='" +
        startY +
        "'></td>\
                    <td><input type='text' class='form-control' readonly name='w' form='coordinate_form' value='" +
        w +
        "'></td>\
                    <td><input type='text' class='form-control' readonly name='h' form='coordinate_form' value='" +
        h +
        "'></td>\
                    <td><input type='text' class='form-control' style='width:250px;' form='coordinate_form' name='label' class='form-control' list='labelOptions'></td>\
                    <td><button class='cross' onclick='removeAnnotation(" +
        id +
        ")'> X </button></td>\
                </tr>"
    );
    coordinates.set(id.toString(), [
      rect.startX,
      rect.startY,
      rect.w,
      rect.h,
      "UNLABELLED",
    ]);
    id++;
  }

  function mouseMove(e) {
    if (drag) {
      ctx.clearRect(0, 0, imgDisplayWidth, imgDisplayHeight);
      ctx.drawImage(imageObj, 0, 0, imgDisplayWidth, imgDisplayHeight);
      for (let i of coordinates.keys()) {
        coordinate = coordinates.get(i.toString());
        ctx.strokeStyle = "green";
        ctx.strokeRect(
          coordinate[0],
          coordinate[1],
          coordinate[2],
          coordinate[3]
        );
      }
      rect.w = e.pageX - this.offsetLeft - rect.startX;
      rect.h = e.pageY - this.offsetTop - rect.startY;
      ctx.strokeStyle = "green";
      ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
    }
  }
  init();
};

function ShowRect(id) {
  ctx.clearRect(0, 0, imgDisplayWidth, imgDisplayHeight);
  ctx.drawImage(imageObj, 0, 0, imgDisplayWidth, imgDisplayHeight);
  for (let i of coordinates.keys()) {
    coordinate = coordinates.get(i.toString());
    ctx.strokeStyle = "green";
    ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
  }
  id = id.toString();
  coordinate = coordinates.get(id);
  var $row = $("tr[id=" + id + "]");
  $tds = $row.find("td:nth-child(5) input[type='text']");
  coordinate[4] = $tds.val();
  if (!coordinate) return;
  ctx.strokeStyle = "red";
  ctx.font = "30px Arial";
  ctx.fillStyle = "#FF0000";
  ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
  ctx.fillText(coordinate[4], coordinate[0], coordinate[1]);
  ctx.lineWidth = 1;
}

function removeAnnotation(id) {
  id = id.toString();
  coordinates.delete(id);
  $("tr[id=" + id + "]").remove();
  ctx.clearRect(0, 0, imgDisplayWidth, imgDisplayHeight);
  ctx.drawImage(imageObj, 0, 0, imgDisplayWidth, imgDisplayHeight);

  for (let i of coordinates.keys()) {
    coordinate = coordinates.get(i.toString());
    ctx.strokeStyle = "green";
    ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
  }
}

function UrlExists(url) {
  var http = new XMLHttpRequest();
  http.open("HEAD", url, false);
  http.send();
  return http.status != 404;
}

function showPage(page_no) {
  console.log("Show page");
  _CURRENT_PAGE = page_no;
  $("#pdf-next, #pdf-prev").attr("disabled", "disabled");
  $("#pdf-current-page").text(page_no);
  imageObj = new Image();
  imageObj.src = "/media/page-" + _CURRENT_PAGE.toString() + ".jpeg";

  if (UrlExists(imageObj.src) == false) {
    if(page_no === 1){
      alert("No PDF Uploaded, Please upload PDF and then continue");
      document.location.replace('upload_pdf');
      return;
    }
    else{
      alert("This is Last Page");
      --_CURRENT_PAGE;  
      showPage(_CURRENT_PAGE);
      $("#pdf-current-page").text(_CURRENT_PAGE);
      $("#pdf-next, #pdf-prev").removeAttr("disabled");
    }
  } else {
    id = 0;
    imageObj.onload = function () {
      canvas.width = 900;
      canvas.height = 1200;
      ctx.clearRect(0, 0, imgDisplayWidth, imgDisplayHeight);
      ctx.drawImage(imageObj, 0, 0, imgDisplayWidth, imgDisplayHeight);

      imgActualHeight = imageObj.height;
      imgActualWidth = imageObj.width;

      console.log("Show page actuals", imgActualWidth, imgActualHeight);
      pageDimensions["Page" + _CURRENT_PAGE.toString()] = [];
      pageDimensions["Page" + _CURRENT_PAGE.toString()].push(imgActualWidth);
      pageDimensions["Page" + _CURRENT_PAGE.toString()].push(imgActualHeight);

      imgDisplayHeight = 1200;
      imgDisplayWidth = 900;
      pagecoors = annotations["Page" + _CURRENT_PAGE.toString()];
      if (typeof pagecoors !== "undefined") {
        for (let i of pagecoors.keys()) {
          coordinate = pagecoors.get(i.toString());
          $("#annotation_table_body").append(
            "<tr id='" +
              i +
              "' onclick='ShowRect(" +
              i +
              ");'>\
                        <td><input type='text' class='form-control' readonly name='startX' form='coordinate_form' value='" +
              coordinate[0] +
              "'></td>\
                        <td><input type='text' class='form-control' readonly name='startY' form='coordinate_form' value='" +
              coordinate[1] +
              "'></td>\
                        <td><input type='text' class='form-control' readonly name='w' form='coordinate_form' value='" +
              coordinate[2] +
              "'></td>\
                        <td><input type='text' class='form-control' readonly name='h' form='coordinate_form' value='" +
              coordinate[3] +
              "'></td>\
                        <td><input type='text' class='form-control' style='width:250px;' form='coordinate_form' name='label' class='form-control' list='labelOptions' value='" +
              coordinate[4] +
              "'></td>\
                        <td><button class='cross' onclick='removeAnnotation(" +
              i +
              ")'> X </button></td>\
                    </tr>"
          );
          coordinates.set(i.toString(), [
            coordinate[0],
            coordinate[1],
            coordinate[2],
            coordinate[3],
            coordinate[4],
          ]);
          ctx.strokeStyle = "green";
          ctx.strokeRect(
            coordinate[0],
            coordinate[1],
            coordinate[2],
            coordinate[3]
          );
          id = Math.max(id, i) + 1;
        }
      }
    };
    $("#pdf-next, #pdf-prev").removeAttr("disabled");
  }
}

function getprev() {
  annotations["Page" + _CURRENT_PAGE.toString()] = new Map();
  curpagecoors = annotations["Page" + _CURRENT_PAGE.toString()];
  if (_CURRENT_PAGE != 1) {
    for (let i of coordinates.keys()) {
      coordinate = coordinates.get(i.toString());
      var $row = $("tr[id=" + i + "]");
      $tds = $row.find("td:nth-child(5) input[type='text']");
      coordinate[4] = $tds.val();
      $row.remove();
      curpagecoors.set(i.toString(), [
        coordinate[0],
        coordinate[1],
        coordinate[2],
        coordinate[3],
        coordinate[4],
      ]);
    }
    for (let i of coordinates.keys()) {
      id = i.toString();
      coordinates.delete(id);
    }
    showPage(--_CURRENT_PAGE);
  } else alert("This is First Page");
}

// Next page of the PDF
function getnex() {
  annotations["Page" + _CURRENT_PAGE.toString()] = new Map();
  curpagecoors = annotations["Page" + _CURRENT_PAGE.toString()];
  for (let i of coordinates.keys()) {
    coordinate = coordinates.get(i.toString());
    var $row = $("tr[id=" + i + "]");
    $tds = $row.find("td:nth-child(5) input[type='text']");
    coordinate[4] = $tds.val();
    $row.remove();
    curpagecoors.set(i.toString(), [
      coordinate[0],
      coordinate[1],
      coordinate[2],
      coordinate[3],
      coordinate[4],
    ]);
  }
  for (let i of coordinates.keys()) {
    id = i.toString();
    coordinates.delete(id);
  }
  showPage(++_CURRENT_PAGE);
}

function exportTableToExcel() {
  annotations["Page" + _CURRENT_PAGE.toString()] = new Map();
  curpagecoors = annotations["Page" + _CURRENT_PAGE.toString()];
  for (let i of coordinates.keys()) {
    coordinate = coordinates.get(i.toString());
    var $row = $("tr[id=" + i + "]");
    $tds = $row.find("td:nth-child(5) input[type='text']");
    coordinate[4] = $tds.val();
    curpagecoors.set(i.toString(), [
      coordinate[0],
      coordinate[1],
      coordinate[2],
      coordinate[3],
      coordinate[4],
    ]);
  }
  console.log(pageDimensions)
  output = new Map();
  for (var i in annotations) {
    output[i] = [];
    for (let j of annotations[i]){
      let tempmap = new Map();
      x = j[1];
      tempmap['width'] = x[2];
      tempmap['height'] = x[3];
      tempmap['left'] = x[0];
      tempmap['top'] = x[1];
      tempmap['label'] = x[4];
      output[i].push(tempmap);
    }
    let tempmap = new Map();
    tempmap["IMAGE_ACTUAL_WIDTH"] = pageDimensions[i][0];
    tempmap["IMAGE_ACTUAL_HEIGHT"] = pageDimensions[i][1];
    output[i].push(tempmap);
  }
  if (document.getElementById("noofcolumns").value < 0) {
    alert("Number of Columns cannot be negative");
    return;
  }
  console.log(output)
  output["ncols"] = document.getElementById("noofcolumns").value;
  var string = JSON.stringify(output);
  //create a blob object representing the data as a JSON string
  var file = new Blob([string], {
    type: "application/json",
  });
  // trigger a click event on an <a> tag to open the file explorer
  var a = document.createElement("a");
  a.href = URL.createObjectURL(file);
  a.download = "data.json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
