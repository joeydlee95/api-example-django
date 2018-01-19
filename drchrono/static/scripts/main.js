function scheduleUpdate(url) {
    $.ajax({
        type: "GET",
        url: url, // hardcoded
        success: function(data){
            var main_div = document.createElement("div");
            main_div.classList.add('list-group')
            var elem = document.getElementById("schedule");
            for (var i = 0; i < data['appointments'].length; i++) {
                var para1 = document.createElement("p");
                var node1 = document.createTextNode("Patient Name: " + data['appointments'][i]['patient']);
                para1.appendChild(node1);

                var para2 = document.createElement("p");
                var node2 = document.createTextNode("Scheduled Time: " + data['appointments'][i]['scheduled_time']);
                para2.appendChild(node2);

                var para3 = document.createElement("p");
                var node3 = document.createTextNode("Exam Room: " + data['appointments'][i]['exam_room']);
                para3.appendChild(node3);

                var para4 = document.createElement("p");
                var node4 = document.createTextNode("Duration: " + data['appointments'][i]['duration']);
                para4.appendChild(node4);

                var para5 = document.createElement("p");
                var node5 = document.createTextNode("Status: " + data['appointments'][i]['status']);
                para5.appendChild(node5);

                var inside_div = document.createElement("div");
                inside_div.classList.add('list-group-item')
                inside_div.appendChild(para1);
                inside_div.appendChild(para2);
                inside_div.appendChild(para3);
                inside_div.appendChild(para4);
                inside_div.appendChild(para5);

                if (data['appointments'][i]['status'] == "Arrived" && data['appointments'][i]['checkin_time'] != "") {
                    var para6 = document.createElement("p");
                    var node6 = document.createTextNode("Checked in: " + data['appointments'][i]['checkin_time']);
                    para6.appendChild(node6);

                    var para7 = document.createElement("p");
                    var node7 = document.createTextNode("Wait Time: " + data['appointments'][i]['wait_time']);
                    para7.appendChild(node7);
                    inside_div.appendChild(para6);
                    inside_div.appendChild(para7);
                }

                if (data['appointments'][i]['status'] == "Arrived") {
                  var para8 = document.createElement("button");
                  para8.onclick = function () {
                    seePatient(data['appointments'][i]['id'], data['appointments'][i]['patient']);
                  };
                  var node8 = document.createTextNode("See Now");
                  para8.appendChild(node8);
                  inside_div.appendChild(para8);
                }

                main_div.appendChild(inside_div)
            }
            elem.appendChild(main_div)
           }
    });
    setTimeout(function() {scheduleUpdate(url); }, 60000);
};

function averageWait(url) {
    $.ajax({
        type: "GET",
        url: url,
        success: function(data){
            document.getElementById("schedule").innerHTML = data['wait_time'];
        }
    });
}