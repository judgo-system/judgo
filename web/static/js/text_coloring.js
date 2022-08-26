

function ingest_tags(text, cooked_tags){

    var cooked_text = text
    
    for(let k=cooked_tags.length-1; k >= 0; k--){
        cooked_text = cooked_text.substring(0, cooked_tags[k][0]) 
        + "<mark style='background: "+ cooked_tags[k][2] +"!important'>"
        + cooked_text.substring(cooked_tags[k][0], cooked_tags[k][1]) 
        +"</mark>"
        + cooked_text.substring(cooked_tags[k][1]);
    }   
    return cooked_text
}

function get_tags_range(text, raw_tags){
    var marked_range = []

    for(const item in raw_tags){
        var query = new RegExp(item, "gim"); 
        
        while (match = query.exec(text)) {
            marked_range.push([match.index, query.lastIndex, raw_tags[item]]);
        }
    } 
    
    // sort based on starting then ending index
    marked_range = marked_range.sort(function(a, b) {
        if (a[0] == b[0]) {
            return b[1] - a[1];
        }
        return a[0] - b[0];
        });
    return marked_range;
}

function get_flat_tags(cooked_tags){
    if (cooked_tags.length == 0){
        return []
    }
    var flat_tags = []
    flat_tags.push(cooked_tags[0])
    
    for(let i=1; i < cooked_tags.length; i++){
        const last_element = flat_tags.at(-1)
        var start = cooked_tags[i][0]
        var end = cooked_tags[i][1]
        if (last_element[1] >= end){
            // next interval is inside or equal to the previous interval so it will be eaten by the larger one.
            continue
        }
        if(last_element[1] > start){
            flat_tags.push([last_element[1], end, cooked_tags[i][2]])
        }else{
            flat_tags.push(cooked_tags[i])
        }
    }

    return flat_tags
}



function get_flat_highlight(cooked_highlight){
    
    cooked_highlight = cooked_highlight.sort(function(a, b) {
        if (a[0] == b[0]) {
            return b[1] - a[1];
        }
        return a[0] - b[0];
    });

    var flat_list = []
    flat_list.push(cooked_highlight[0])
    
    for(let i=1; i < cooked_highlight.length; i++){
        const last_element = flat_list.at(-1)
        var start = cooked_highlight[i][0]
        var end = cooked_highlight[i][1]
        if (last_element[1] >= end){
            // next interval is inside or equal to the previous interval so it will be eaten by the larger one.
            continue
        }
        if(last_element[1] > start){
            flat_list[flat_list.length-1][1] = end
        }else{
            flat_list.push(cooked_highlight[i])
        }
    }

    return flat_list
}


function update_highlight_list(highlight_list, start, end){

    // if the highlight was in the highlight range we will remove it 

    // confirm if it's a delete action or not.
    const color = "yellow"
    var index = -1
    var action = ""
    for(let i=0; i< highlight_list.length; i++){
        if (highlight_list[i][0] < start && highlight_list[i][1] > end){             
            highlight_list.push([highlight_list[i][0], start, color])
            highlight_list.push([end, highlight_list[i][1], color])
            action = "delete"
        } else if (highlight_list[i][0] == start && highlight_list[i][1] > end){ 
            
            highlight_list.push([end, highlight_list[i][1], color])
            action = "delete"
        } else if (highlight_list[i][1] == start && highlight_list[i][1] < end){ 
            
            highlight_list.push([highlight_list[i][0], end, color])
            action = "delete"
        } else if (highlight_list[i][0] < start && highlight_list[i][1] == end){ 
            highlight_list.push([highlight_list[i][0], start, color])
            action = "delete"
        } else if (highlight_list[i][0] == start && highlight_list[i][1] == end){ 
            action = "delete"
        }     
        if (action =="delete"){
            index = i
            break
        }    
    }
    if (index != -1){
        highlight_list.splice(index, 1)           
    }
    if (action=="delete"){
        return highlight_list
    }
    highlight_list.push([start, end, color])

    return get_flat_highlight(highlight_list)
}



function get_flat_html_elements(highlights, tags){
    
    var cooked_highlight = []
    cooked_highlight.push(...highlights)
    if (tags.length != 0){
        cooked_highlight.push(...tags)
    }
    cooked_highlight = cooked_highlight.sort(function(a, b) {
        if (a[0] == b[0]) {
            return b[1] - a[1];
        }
        return a[0] - b[0];
    });

    var flat_list = []
    flat_list.push(cooked_highlight[0])
    
    for(let i=1; i < cooked_highlight.length; i++){
        const last_element = flat_list.at(-1)
        var start = cooked_highlight[i][0]
        var end = cooked_highlight[i][1]
        if (last_element[1] >= end){
            // next interval is inside or equal to the previous interval so it will be eaten by the larger one.
            continue
        }
        if(last_element[1] > start){
            flat_list[flat_list.length-1][1] = start
        }
        flat_list.push(cooked_highlight[i])
    }
    return flat_list
}



function get_cooked_text(text, raw_tags, flat_highlights){

    var flat_tags = []
    if(Object.keys(raw_tags).length != 0){
        var cooked_tags =  get_tags_range(text, raw_tags)
        flat_tags = get_flat_tags(cooked_tags)
    }

    if(flat_tags.length ==0 && flat_highlights.length ==0){
        return text
    }
    var flat_element = get_flat_html_elements(flat_highlights, flat_tags)
    var cooked_text = ingest_tags(text, flat_element)
    return cooked_text
}

// function get_cooked_text(text, raw_tags, raw_highlight){

//     var cooked_tags =  get_tags_range(text, raw_tags)
//     if(cooked_tags.length ==0){
//         return text
//     }
    
//     var flat_tags = get_flat_tags(cooked_tags)
//     var cooked_text = ingest_tags(text, flat_tags)
//     return cooked_text
// }

// function highlight_tags(search_area, tag){
    
    
//     if (tag.length <2) return
    
//     // in the case there is more than one word in tag
//     tags = tag.split("|")
//     tag = tags[0]
//     color = tags[1]

//     splited = tag.split(" ")
//     if (splited.length > 1){
//         temp = ""
//         for (let i = 0; i < splited.length; i++) { 
//            if(i ==splited.length || i ==0){
//             temp += splited[i]
//            }else{
//             temp += "[^a-zA-Z\d]" + splited[i]
//            }
//         }
//         tag = temp
//     }

    
//     var textarea = $(search_area);    
//     var query = new RegExp("("+tag+")", "gim"); 
    
//     const markTag = "<mark style='background: "+ color +"!important'>"
//     newtext= textarea.html().replace(query, markTag+"$1</mark>");    
//     textarea.html(newtext);
// }


// function dehighlight_tags(search_area, tag, second){

//     // var index = input_tags.indexOf(tag);
//     // if (index !== -1) {
//     //     input_tags.splice(index, 1);
//     // }
//     // input_tags.push(tag)
//     tags = tag.split("|")
//     tag = tags[0]
//     color = tags[1]
    
    
//     var textarea = $(search_area);    
//     var enew = ''; 

//     // in the case there is more than one word in tag
//     splited = tag.split(" ")
//     if (splited.length > 1){
//         temp = ""
//         for (let i = 0; i < splited.length; i++) { 
//            if(i ==splited.length || i ==0){
//             temp += splited[i]
//            }else{
//             temp += "[^a-zA-Z\d]" + splited[i]
//            }
//         }
//         tag = temp
//     }

//     var tagColorDic = localStorage['colorDic']
//     var colorList = localStorage['colorList']
//     var isConstColor = false;
    
//     tagColorDic = JSON.parse(tagColorDic);
//     colorList = JSON.parse(colorList);

//     color = tagColorDic[tag.toLowerCase()]
//     if (color == null){
//         // After 20 tags we use a constant color
//         color = "#fa9fb5";
//         isConstColor = true;
//     }
//     if (second == true && !isConstColor){

//         colorList.push(color)
//         delete tagColorDic[tag.toLowerCase()]

//         localStorage['colorList'] = JSON.stringify(colorList);
//         localStorage['colorDic'] = JSON.stringify(tagColorDic);

//     }

//     const markTag = "<mark style=\"background: " +color.replace("(", "\\(").replace(")", "\\)") +"!important\">"    
//     var query = new RegExp("("+markTag+tag+")", "gim");   
//     cases = textarea.html().match(query)
//     if (cases !=null){
//         for (let i = 0; i < cases.length; i++) { 
//             t = cases[i].replace(markTag.replace("\\(", "(").replace("\\)",")"),"");
//             t = t.replace("</mark>","");
//             newtext= textarea.html().replace(cases[i], t);    
//             textarea.html(newtext); 
//         }
//     }
// }