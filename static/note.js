if (window.innerWidth < 4000) {
    document.querySelectorAll(".notediv").forEach(notediv => {
        notediv.style.width = "32%";
    });
    document.querySelectorAll(".notediv")
}
if (window.innerWidth < 1220) {
    document.querySelectorAll(".notediv").forEach(notediv => {
        notediv.style.width = "48.3%";
    });
    document.querySelectorAll(".notediv")
}
if (window.innerWidth < 1000) {
    document.querySelectorAll(".notediv").forEach(notediv => {
        notediv.style.width = "98%";
    });
    document.querySelectorAll(".notediv")
}
if (window.innerWidth < 600) {
    document.querySelector("#taginputgroup").style.paddingLeft = "0";
}
window.addEventListener('resize', function () {
    if (window.innerWidth < 1420) {
        document.querySelectorAll(".notediv").forEach(notediv => {
            notediv.style.width = "32%";
        });
        document.querySelectorAll(".notediv")
    }
    if (window.innerWidth < 1220) {
        document.querySelectorAll(".notediv").forEach(notediv => {
            notediv.style.width = "48.3%";
        });
        document.querySelectorAll(".notediv")
    }
    if (window.innerWidth < 1000) {
        document.querySelectorAll(".notediv").forEach(notediv => {
            notediv.style.width = "98%";
        });
        document.querySelectorAll(".notediv")
    }
    if (window.innerWidth < 700) {
        document.querySelector("#taginputgroup").style.paddingLeft = "0";
    }
    else {
        document.querySelector("#taginputgroup").style.paddingLeft = "40%";
    }
});

noteIput = document.querySelector("#noteinbox")
tagIput = document.querySelector("#taginbox")
searchIput = document.querySelector("#searchinbox")

notesElement = document.querySelector("#allnotes");

saveButton = document.querySelector("#savenotebtn")

searchButton = document.querySelector("#searchnotebtn")

saveButton.addEventListener("click", function (evnet) {
    //stop default action
    event.preventDefault();
    //check if empty
    if (!noteIput.value) {
        noteIput.placeholder = "☹take some note first!"
        setTimeout(() => {
            noteIput.placeholder = "click here take some note now!"
        }, 4000);
        return
    }
    if (!tagIput.value) {
        tagIput.placeholder = "☹need input a tag"
        setTimeout(() => {
            tagIput.placeholder = "TAG"
        }, 4000);
        return
    }
    if(tagIput.value.length>20){
        alert("☹tag too long,not a tag like this");
        return;
    }

    saveButton.disabled = true;
    saveButton.innerText = "Saving.."
    setTimeout(function () {
        saveButton.disabled = false;
    }, 8000);


    xhr = new XMLHttpRequest();
    xhr.open("POST", '/savenote', true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.responseType = 'text';
    xhr.onreadystatechange = function() { // Call a function when the state changes.
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200 && this.response) {
            // Request finished. Do processing here.
            
            notesElement.innerHTML = `<div class="notediv">
                                                <p> saved </p>
                                                <textarea rows="5">{noteIput.value}</textarea>
                                                <p class="tagtext">{tagIput.value}</p>
                                           </div>`  + notesElement.innerHTML;
                saveButton.innerText = "Saved";
                tagIput.value=this.response;
        }
        else{
            
        }
    }
    xhr.send(`usertag=${tagIput.value}&usernote=${noteIput.value}`);
    $.post("/savenote",
        {
            usertag: tagIput.value,
            usernote: noteIput.value
        },
        (function (response) {

            if (response == true) {
                notesElement.innerHTML = `<div class="notediv">
                                                <p> saved </p>
                                                <textarea rows="5">{noteIput.value}</textarea>
                                                <p class="tagtext">{tagIput.value}</p>
                                           </div>`  + notesElement.innerHTML;
                saveButton.innerText = "Saved";
                tagIput.value="";
            }
            else {
                notesElement.innerHTML = `<div class="notediv" >
                                                <p> failed </p>
                                                <textarea rows="5">try again</textarea>
                                                <p class="tagtext">error</p>
                                           </div>`  + notesElement.innerHTML;
            }
            setTimeout(function () {
                saveButton.textContent = "Save";
            }, 4000);
        }))
})

searchButton.addEventListener("click", function (evnet) {
    //stop default action
    event.preventDefault();

    if (!searchIput.value) {
        searchIput.placeholder = "☹ input a keyword"
        setTimeout(() => {
            searchIput.placeholder = "search"
        }, 4000);
        return
    }
    searchButton.textContent = "Searching.."
    searchButton.disabled = true;
    setTimeout(function () {
        searchButton.disabled = false;
    }, 4000);
    nResult = 0;
    $.get("/searchnote",
        { keyword: $("#searchinbox").val() },
        (function (response) {
            notelist = response;
            notesElement.innerHTML = ""
            notelist.forEach(function (anote) {
                notesElement.innerHTML = notesElement.innerHTML + `<div class="notediv" id="notediv${anote[2]}">
                                            <textarea rows="5">${anote[1]}</textarea>
                                            <p class="tagtext"><button class="zoombtn" onclick="zoom()" zoomed="false" value="${anote[2]}">🍳+</button> ${anote[0]}</p>
                                          </div>`;
                nResult += 1;
            });
            notesElement.innerHTML = `<p class="notice">Found ${nResult} note(s): ` + notesElement.innerHTML;
            searchButton.textContent = "Searched"
            setTimeout(function () {
                searchButton.textContent = "Search";
            }, 4000);
        }))
})


oldSize = document.querySelector(".notediv").style.width;
function zoom() {
    noteid = "#" + "notediv" + event.srcElement.value
    console.log(noteid)
    note = document.querySelector(noteid)

    if (event.srcElement.zoomed) {
        event.srcElement.zoomed = false;
        event.srcElement.textContent = "🍳+";
        note.style.width = oldSize;
        note.firstElementChild.rows = "5";
        note.firstElementChild.style.overflow = "hidden";
    }
    else {
        event.srcElement.zoomed = true;
        event.srcElement.textContent = "🍳-";
        note.style.width = "98%";
        note.firstElementChild.rows = "13";
        note.firstElementChild.style.overflow = "visible";
    }
}