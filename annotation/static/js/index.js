

window.onload = function() {

    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    prev = document.getElementById('pdf-prev');
    next = document.getElementById('pdf-next');
    rect = {};
    drag = false;
    imageObj = null;
    coordinates = new Map();
    annotations = new Map();
    id = 0;
    var _CURRENT_PAGE = 1;
       

    function init() {
        canvas.addEventListener('mousedown', mouseDown, false);
        canvas.addEventListener('mouseup', mouseUp, false);
        canvas.addEventListener('mousemove', mouseMove, false);
        prev.addEventListener('click',getprev,false);
        next.addEventListener('click', getnex, false);
        _CURRENT_PAGE = 1;
        showPage(1);
    }

    function mouseDown(e) {
        rect.startX = e.pageX - this.offsetLeft;
        rect.startY = e.pageY - this.offsetTop;
        drag = true;
    }

    function mouseUp() { 
        drag = false; 
        var annotation_table_body = document.getElementById("annotation_table_body");
            $("#annotation_table_body").append(
                "<tr id='"+id+"' onclick='ShowRect("+id+");'>\
                    <td><input type='text' class='form-control' readonly name='startX' form='coordinate_form' value='"+rect.startX+"'></td>\
                    <td><input type='text' class='form-control' readonly name='startY' form='coordinate_form' value='"+rect.startY+"'></td>\
                    <td><input type='text' class='form-control' readonly name='w' form='coordinate_form' value='"+rect.w+"'></td>\
                    <td><input type='text' class='form-control' readonly name='h' form='coordinate_form' value='"+rect.h+"'></td>\
                    <td><input type='text' class='form-control' style='width:250px;' form='coordinate_form' name='label' class='form-control' list='labelOptions'></td>\
                    <td><button class='cross' onclick='removeAnnotation("+id+")'> X </button></td>\
                </tr>"
            );
        coordinates.set(id.toString(),[rect.startX,rect.startY,rect.w,rect.h,""]);
        id++;
    }

    function mouseMove(e) {
        if (drag) {
            ctx.clearRect(0, 0, 900, 1200);                
            ctx.drawImage(imageObj, 0, 0);   
            
            for(let i of coordinates.keys())
            {
                coordinate = coordinates.get(i.toString());
                
                ctx.strokeStyle = 'red';
                ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
            }             
            rect.w = (e.pageX - this.offsetLeft) - rect.startX;
            rect.h = (e.pageY - this.offsetTop) - rect.startY;
            ctx.strokeStyle = 'red';
            ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);                
        }
    }

    
//
    init();
}

function ShowRect(id)
{
    ctx.clearRect(0, 0, 900, 1200);                
    ctx.drawImage(imageObj, 0, 0);   
    
    for(let i of coordinates.keys())
    {
        coordinate = coordinates.get(i.toString());
        
        ctx.strokeStyle = 'red';
        ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
    }             
    id = id.toString();
    coordinate = coordinates.get(id);
    if(!coordinate)
        return;
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'green';
    ctx.strokeRect(coordinate[0],coordinate[1],coordinate[2],coordinate[3]);
    ctx.lineWidth = 1;
}

function removeAnnotation(id)
{
    id = id.toString();
    coordinates.delete(id);
    $("tr[id="+id+"]").remove();
    ctx.clearRect(0, 0, 900, 1200);                
    ctx.drawImage(imageObj, 0, 0);   
    
    for(let i of coordinates.keys())
    {
        coordinate = coordinates.get(i.toString());
        
        ctx.strokeStyle = 'red';
        ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
    }
    
}

function UrlExists(url) {
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status != 404;
}

function showPage(page_no) {
    _CURRENT_PAGE = page_no;

    // Disable Prev & Next buttons while page is being loaded
    $("#pdf-next, #pdf-prev").attr('disabled', 'disabled');

    // While page is being rendered hide the canvas and show a loading message
    

    // Update current page in HTML
    $("#pdf-current-page").text(page_no);
    
    // Fetch the page
    
    imageObj = new Image();
    imageObj.src = '/media/page-' + _CURRENT_PAGE.toString() + '.jpeg';
    if(UrlExists(imageObj.src)==false){
        --_CURRENT_PAGE;
        showPage(_CURRENT_PAGE);
        $("#pdf-current-page").text(_CURRENT_PAGE);
        $("#pdf-next, #pdf-prev").removeAttr('disabled');
    }
    else{
        id=0;
        imageObj.onload = function () {
        canvas.width = 900;
        canvas.height = 1200;
        ctx.clearRect(0, 0, 900, 1200);
        ctx.drawImage(imageObj, 0, 0);
        pagecoors = annotations['Page' + _CURRENT_PAGE.toString()];
        if(typeof pagecoors !== 'undefined'){
            for (let i of pagecoors.keys()) {
                coordinate = pagecoors.get(i.toString());
                $("#annotation_table_body").append(
                    "<tr id='" + i + "' onclick='ShowRect(" + i + ");'>\
                        <td><input type='text' class='form-control' readonly name='startX' form='coordinate_form' value='"+ coordinate[0] + "'></td>\
                        <td><input type='text' class='form-control' readonly name='startY' form='coordinate_form' value='"+ coordinate[1]+ "'></td>\
                        <td><input type='text' class='form-control' readonly name='w' form='coordinate_form' value='"+ coordinate[2]+ "'></td>\
                        <td><input type='text' class='form-control' readonly name='h' form='coordinate_form' value='"+ coordinate[3]+ "'></td>\
                        <td><input type='text' class='form-control' style='width:250px;' form='coordinate_form' name='label' class='form-control' list='labelOptions' value='"+ coordinate[4]+"'></td>\
                        <td><button class='cross' onclick='removeAnnotation("+ i + ")'> X </button></td>\
                    </tr>"
                )
                coordinates.set(i.toString(), [coordinate[0], coordinate[1], coordinate[2], coordinate[3],coordinate[4]]);
                ctx.strokeStyle = 'red';
                ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
                id = Math.max(id,i)+1;
            }
        }
        };
        $("#pdf-next, #pdf-prev").removeAttr('disabled');
    }
}

function getprev() {
    annotations['Page' + _CURRENT_PAGE.toString()] = new Map();
    curpagecoors = annotations['Page' + _CURRENT_PAGE.toString()];
    if (_CURRENT_PAGE != 1){
        for (let i of coordinates.keys()) {
            coordinate = coordinates.get(i.toString());
            var $row = $("tr[id=" + i + "]");
            $tds = $row.find("td:nth-child(5) input[type='text']");
            coordinate[4] = $tds.val();
            $row.remove();
            curpagecoors.set(i.toString(), [coordinate[0], coordinate[1], coordinate[2], coordinate[3], coordinate[4]]);
        }
        for (let i of coordinates.keys()) {
            id = i.toString();
            coordinates.delete(id);
        }
        showPage(--_CURRENT_PAGE);
    }
};

// Next page of the PDF
function getnex() {
    annotations['Page' + _CURRENT_PAGE.toString()] = new Map();
    curpagecoors = annotations['Page' + _CURRENT_PAGE.toString()];
    for (let i of coordinates.keys()) {
        coordinate = coordinates.get(i.toString());
        var $row = $("tr[id=" + i + "]");
        $tds = $row.find("td:nth-child(5) input[type='text']");
        coordinate[4] = $tds.val(); 
        $row.remove();
        curpagecoors.set(i.toString(), [coordinate[0], coordinate[1], coordinate[2], coordinate[3], coordinate[4]]);
    }
    for (let i of coordinates.keys()) {
        id = i.toString();
        coordinates.delete(id);
    }
    showPage(++_CURRENT_PAGE);
};

function exportTableToExcel() {
    annotations['Page' + _CURRENT_PAGE.toString()] = new Map();
    curpagecoors = annotations['Page' + _CURRENT_PAGE.toString()];
    for (let i of coordinates.keys()) {
        coordinate = coordinates.get(i.toString());
        var $row = $("tr[id=" + i + "]");
        $tds = $row.find("td:nth-child(5) input[type='text']");
        coordinate[4] = $tds.val();
        curpagecoors.set(i.toString(), [coordinate[0], coordinate[1], coordinate[2], coordinate[3], coordinate[4]]);
    }
    output = new Map();
    for (var i in annotations) {
        output[i] = [];
        for (let j of annotations[i]){
            let tempmap = new Map();
            x = j[1];
            tempmap['width'] = x[2];
            tempmap['height'] = x[1];
            tempmap['left'] = x[0];
            tempmap['top'] = x[1];
            output[i].push(tempmap);
        }
    }
    var string = JSON.stringify(output);
    //create a blob object representing the data as a JSON string
    var file = new Blob([string], {
        type: 'application/json'
    });
    // trigger a click event on an <a> tag to open the file explorer
    var a = document.createElement('a');
    a.href = URL.createObjectURL(file);
    a.download = 'data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
