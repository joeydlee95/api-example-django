function scheduleUpdate(url, doctor_id) {
    $.ajax({
        type: "GET",
        url: url, // hardcoded
        success: function(data){
            var main_div = document.createElement("div");
            main_div.classList.add('list-group');
            var elem = document.getElementById("schedule");
            var elem2 = document.getElementById("currently-seeing");
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
                  var node4 = document.createTextNode("Duration: " + data['appointments'][i]['duration'] + " minutes");
                  para4.appendChild(node4);

                  var para5 = document.createElement("p");
                  var node5 = document.createTextNode("Status: " + data['appointments'][i]['status']);
                  para5.appendChild(node5);

                  var inside_div = document.createElement("div");

                  inside_div.classList.add('list-group-item');
                  if(data['appointments'][i]['is_currently_seen']) {
                    inside_div.classList.add('list-group-item-success');

                  }
                  inside_div.appendChild(para1);
                  inside_div.appendChild(para2);
                  inside_div.appendChild(para3);
                  inside_div.appendChild(para4);
                  inside_div.appendChild(para5);

                  if (data['appointments'][i]['status'] == "Arrived" && data['appointments'][i]['checkin_time']!= "" && !data['appointments'][i]['is_currently_seen']) {
                      var para6 = document.createElement("p");
                      var node6 = document.createTextNode("Checked in: " + data['appointments'][i]['checkin_time']);
                      para6.appendChild(node6);

                      var para7 = document.createElement("p");
                      var node7 = document.createTextNode("Wait Time: " + data['appointments'][i]['wait_time'] + " minutes");
                      para7.appendChild(node7);
                      inside_div.appendChild(para6);
                      inside_div.appendChild(para7);

                      appt_id = data['appointments'][i]['appointment_id'];
                      patient_id = data['appointments'][i]['patient'];
                      var para8 = document.createElement("button");
                      para8.classList.add('btn');
                      para8.classList.add('btn-secondary');
                      para8.onclick = function() {seePatient(appt_id, patient_id, doctor_id)}
                      var node8 = document.createTextNode("See Now");
                      para8.appendChild(node8);

                      inside_div.appendChild(para6);
                      inside_div.appendChild(para7);
                      inside_div.appendChild(para8);
                  }

                  main_div.appendChild(inside_div);
            }
            elem.appendChild(main_div);
        },
    });
    //setTimeout(function() {scheduleUpdate(url, doctor_id); }, 60000);
};

function averageWait(url) {
    $.ajax({
        type: "GET",
        url: url,
        success: function(data){
            document.getElementById("averageWait").innerHTML = "";
            var main_div = document.createElement("div");
            var elem = document.getElementById("averageWait");
            var node = document.createTextNode("Average wait time: " + data['wait_time'] + " minutes");
            var para = document.createElement("p");
            para.appendChild(node);
            main_div.appendChild(para);
            elem.appendChild(main_div);
        }
    });
}

function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function seePatient(id, full_name, doctor_id) {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
    });
    var str = "Do you want to see " + full_name;
    var r = confirm(str);
    if (r == true) {
      var url = "/schedule/" + doctor_id + "/";
      $.ajax({
         type: "POST",
         url: url,
         data: {
                'operation': 'seePatient',
                'appointment_id': id, // from form
                },
         success: function(){

             document.getElementById('currently-seeing').innerHTML = "Now seeing " + full_name;
             new_url = "/scheduleupdate/" + doctor_id + "/";
             scheduleUpdate(new_url, doctor_id);
         }
      });
    }
    else {
      return;
    }
  }
