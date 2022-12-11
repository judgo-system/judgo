
function getCaretCharacterOffsetWithin(element) {
    var caretOffset = 0;
    var doc = element.ownerDocument || element.document;
    var win = doc.defaultView || doc.parentWindow;
    var sel;
    if (typeof win.getSelection != "undefined") {
        sel = win.getSelection();
        if (sel.rangeCount > 0) {
        var range = win.getSelection().getRangeAt(0);
        var preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length;
        }
    } else if ((sel = doc.selection) && sel.type != "Control") {
        var textRange = sel.createRange();
        var preCaretTextRange = doc.body.createTextRange();
        preCaretTextRange.moveToElementText(element);
        preCaretTextRange.setEndPoint("EndToEnd", textRange);
        caretOffset = preCaretTextRange.text.length;
    }
    return caretOffset;
}


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
    // In this function we merge highlited range
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
    // In this function, tags elements have higher priority over highlighting by mouse
    var cooked_highlight = []
    cooked_highlight.push(...JSON.parse(JSON.stringify(highlights)))
 
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
            if(last_element[2]!='yellow'){
                // next interval is inside or equal to the previous interval so it will be eaten by the larger one.
                continue
            }
            else{
                var extended_highlight = [end, last_element[1], last_element[2]] 
                flat_list[flat_list.length-1][1] = start

                flat_list.push(cooked_highlight[i])
                if( end < extended_highlight[1]){
                    flat_list.push(extended_highlight)
                    
                }
                continue
            }
        }
        
        if(last_element[1] > start){
            flat_list[flat_list.length-1][1] = start
        }
        flat_list.push(cooked_highlight[i])
    }
    return flat_list
}


function get_cooked_full_text(text, raw_tags, flat_highlights){

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



// FONT CHANGE FUNCTION
function changeFontSize(direction, element){
    // get an element and change its font according to given direction
    // direction could be negative or positive for increasing and decreading font respectively.
    var element = document.getElementById(element);
    style = window.getComputedStyle(element, null).getPropertyValue('font-size');
    currentSize = parseFloat(style);
    element.style.fontSize = (currentSize + direction) + 'px';
}
