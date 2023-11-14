
let isProcessing = false;

const csrfToken = $("meta[name='csrf']").attr("content");
const inputFile = $("#input-file");
const fileInfomatoinSpan = $("#file-infomation");
const videoDownloadDiv = $("#video-download-link");
const $dataTable = $("#data-table tbody");
const $dataTableHeader = $("#data-table thead");
const VIDEO_TIME_THRESHOLD_MS = 200; // 현재 시간의 +- 임계 기준값
let video;
let tableHeader = undefined;
let setHeader = false;
let poseData = undefined;

$("#send-video").click(processingVideo);

function processingVideo(){
    if (isProcessing){
        // if when video is processing, block action
        alert("이미 영상이 처리 중입니다.");
        return false;
    }
    
    const file = inputFile[0].files;
        
    // Valid file length
    if (file.length == 0){
        alert("파일을 첨부해 주세요.");
        return false;
    }

    isProcessing = true;
    const formData = new FormData();

    // Display file infomation 
    fileInfomatoinSpan.html(`
        파일 크기: ${Math.round(file[0].size / (1024 * 1024), 2)}MB<br>
        *파일 크기가 클 경우에 처리 시간이 오래 걸릴 수 있습니다.
    `)

    createLoading();
    
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('file', file[0]);

    $.ajax({
        type : 'POST',
        data : formData,
        processData: false,
        contentType: false,
        success: function(data) {
            tableHeader = JSON.parse(data.table_header);
            poseData = JSON.parse(data.pose_data);
            videoDownloadDiv.html(`
                <a href="${data.processed_file}" download>영상 다운로드</a> |
                <a href="${data.row_data_file}" download>DATA 다운로드</a> <br/><br/>
                <video id="pose-video" controls src="${data.processed_file}" preload="auto" width="500px" />
            `);
            setVideo();
            setTableHeader(tableHeader);
        },
        error: function(xhr, status, error) {
            console.error('Error uploading file:', error);
        },
        complete : function(){
            isProcessing = false;
            removeLoading();
        }
    });
}


function setVideo(){
    video = document.getElementById("pose-video");
    video.addEventListener("timeupdate", timeUpdateListener);
}

/*
    현재 current time이 주어졌을 때,
    해당 current time에 해당하는 데이터를 보여줘야 함.
    -> 정확한 current time이 매칭되지 않을 수 있음.
    ex) 100ms의 데이터가 있으나 current time이 100이 나오지 않을 수 있음.
    0, 0.25, 0.51, 0.58, 0.83
    => Solve 1. 해당 시간의 -+ 0.2초 데이터를 보여줌.
*/

function timeUpdateListener(){
    
    const currentTime = video.currentTime;
    const currentTimeMS = currentTime * 1000;
    
    const data = poseData.filter((x) => {
        if (x[0] > currentTimeMS - VIDEO_TIME_THRESHOLD_MS && 
            x[0] < currentTimeMS + VIDEO_TIME_THRESHOLD_MS){
                return x
            }
    });
    
    updateTable(data);
}

function setTableHeader(header){
    let headerHtml = ``;
    header.map((i, x) => {
        headerHtml += `<th>${i}</th>`;
    });
    $dataTableHeader.html(headerHtml);
    setHeader = true;
}

function updateTable(data){
    /*
        Args:
            data : length 100 data's of X, Y, Z landmarks.
    */
    $dataTable.empty();
    data.map((i, x) => {
        let el = `<tr>`;
        i.map((j, y) => {
            el += `<td>${j}</td>`
        });
        el += `</tr>`; 
        $dataTable.append(el);
    });
}


/*
    loading functions
*/
function createLoading(){
    const loading = $(`<img src='/static/manager/img/loading.svg'
                            style='width : 30px; height : 30px;' >`);
    $(".loading").append(loading);
    return loading;
}

function removeLoading(){
    $(".loading").empty();
}

