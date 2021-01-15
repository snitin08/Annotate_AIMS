

window.onload = function() {

    canvas = document.getElementById('canvas');
    console.log(canvas)
    ctx = canvas.getContext('2d');
    rect = {};
    drag = false;
    imageObj = null;
    coordinates = new Map();
    id = 0;
       

    function init() {
        imageObj = new Image();
        imageObj.onload = function () { ctx.drawImage(imageObj, 0, 0); };
        imageObj.src = '/media/page_1.jpeg';
        console.log(imageObj.src);
        canvas.addEventListener('mousedown', mouseDown, false);
        canvas.addEventListener('mouseup', mouseUp, false);
        canvas.addEventListener('mousemove', mouseMove, false);
    }

    function mouseDown(e) {
        console.log(e.pageX);
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
            )
        coordinates.set(id.toString(),[rect.startX,rect.startY,rect.w,rect.h]);
        id++;
        console.log(coordinates);
        
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
    ctx.strokeStyle = 'red';
    ctx.strokeRect(coordinate[0],coordinate[1],coordinate[2],coordinate[3]);
    ctx.lineWidth = 1;
}

function removeAnnotation(id)
{
    
    id = id.toString();

    coordinates.delete(id);
    $("tr[id="+id+"]").remove()
    ctx.clearRect(0, 0, 900, 1200);                
    ctx.drawImage(imageObj, 0, 0);   
    
    for(let i of coordinates.keys())
    {
        coordinate = coordinates.get(i.toString());
        
        ctx.strokeStyle = 'red';
        ctx.strokeRect(coordinate[0], coordinate[1], coordinate[2], coordinate[3]);
    }
    
}
