
// $('#exactId')

/*
function fillSkill(query) {

    value = encodeURI((query))
    value = query.toString();
    console.log((value))
    
}

function renderSkills(data) {
    html = ''
    for(var i = 0; i < data.length; i++) {
        //console.log(name + url)
'<input id=button'
        html += '<a href="'+url+'">'+name+'</a> <br> '
        //console.log(html)
    }
    return $(html)
}
*/

function insertConnections(data){
    //console.log(data[0][0]);
    $('#connections').html(renderData(data))
    
}

function fillSearch(query,label,keyword0) {

    console.log(("fillSearch"));
    console.log((keyword0))
    console.log((query));
    value = encodeURI((query))
    value = query.toString();
    console.log((value))

    console.log((parseInt(label)))

    if (parseInt(label)>0) {
        for(var i=1; i<6; i++){
            if (i==parseInt(label)){
            document.getElementById("button"+i).style.background = "green";
            }
            else{
            document.getElementById("button"+i).style.background = "";
            }
        }
    }
    
    //$.get('/search_get',{skills:value}, function(jresult) {
    $.getJSON('/search_get',{skills:value,keyword:keyword0}, function(jresult) {
          result= eval(jresult);
        //result= jresult;
          //console.log("Output is = " + result.connection);
          //console.log(result.connection[0][0]);
          //console.log(result.connection[0][1]);
          /*for(var i = 0; i < 6; i++) {
              $('#connection_'+i).html(result.connection[i][0])
              $('#connection_url_'+i).html(result.connection[i][1])
              $('#leader_'+i).html(result.leader[i][0])
              $('#leader_url_'+i).html(result.leader[i][1])
              $('#group_'+i).html(result.group[i][0])
              $('#group_url_'+i).html(result.group[i][1])
              
              insertConnections(result.connection[i][0],result.connection[i][1])
              insertLeaders(result.leader[i][0],result.leader[i][1])
              insertGroups(result.group[i][0],result.group[i][1])
              }*/
              insertConnections(result.connection)
              insertLeaders(result.leader)
              insertGroups(result.group)

              });
}

function renderConnections(data) {
    html = ''
    for(var i = 0; i < data.length; i++) {
        //console.log(i)
        name = data[i][0]
        url = data[i][1]
        id = data[i][2]
        //console.log(name + url)
        //html += '<a href="'+url+'">'+name+'</a> <br> '
        //html += '<a href="'+url+'" onmouseover="get_cpic('+id+')" onmouseout="get_cpic('+data[0][2]+')">'+name+' </a> <br> '
        //html += '<li class="list-group-item" href="'+url+'" onmouseover="get_cpic('+id+')" onmouseout="get_cpic('+data[0][2]+')">'+name+' </li> '
        //html += '<a href="'+url+'" onmouseover="get_cpic('+id+')" onmouseout="get_cpic('+data[0][2]+')">'+name+' </a> <br> '
        html += '<a href="'+url+'" onmouseover="get_cpic('+id+')" onmouseout="get_cpic('+data[0][2]+')"><big>'+name+' </big></a> <br> '
        console.log(html)
    }
    return $(html)
}

function insertConnections(data){
    //console.log(data[0][0]);
    $('#connections').html(renderConnections(data))
    //if (data[0]){
    try{
        get_cpic(data[0][2]);
    }
    catch(err){
        get_cpic("00000");
    }
}


function renderLeaders(data) {
    html = ''
    for(var i = 0; i < data.length; i++) {
        //console.log(i)
        name = data[i][0]
        url = data[i][1]
        id = data[i][2]
        //console.log(name + url)
        //html += '<a href="'+url+'">'+name+'</a> <br> '
        html += '<a href="'+url+'" onmouseover="get_lpic('+id+')" onmouseout="get_lpic('+data[0][2]+')" ><big>'+name+'</big></a> <br>'
        //html += '<li class="list-group-item" href="'+url+'" onmouseover="get_lpic('+id+')" onmouseout="get_lpic('+data[0][2]+')" >'+name+' </li>'
        //html += '<a href="'+url+'" onmouseover="get_lpic('+id+')" onmouseout="get_lpic(static/pictures/blank.jpg)" >'+name+' </a> <br> '
        console.log(html)
    }
    return $(html)
}

function insertLeaders(data){
    $('#leaders').html(renderLeaders(data))
    //if (data[0]){
    try{
        get_lpic(data[0][2]);
    }
    catch(err){
        get_lpic("00000");
    }
}

function renderGroups(data) {
    html = ''
    for(var i = 0; i < data.length; i++) {
        //console.log(i)
        name = data[i][0]
        url = data[i][1]
        html += '<a href="'+url+'"><font size="3">'+name+'</font></a> <br>'
        //html += '<li class="list-group-item" href="'+url+'">'+name+'</li>'
        //console.log(html)
    }
    return $(html)
}


function insertGroups(data){
    $('#groups').html(renderGroups(data))
}


function get_cpic(id) {
    $('#cpic').html(get_pic(id))
}

function get_lpic(id) {
    $('#lpic').html(get_pic(id))
}

function get_pic(id){
    html = '<img src="/static/pictures/'+id+'.jpg" name="the_image" border="0" height="100" width="100">'
    return $(html)
}

