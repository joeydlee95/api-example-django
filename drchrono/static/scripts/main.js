/*function see_patient(appointment_id, appointment_name) {
  var fired_button = document.createTextNode(appointment_name);
  var id = document.createTextNode(appointment_id);
  var csrftoken = getCookie('csrftoken');
  var data = {
    'appointment_id': id.value,
  };

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
  });

  $.ajax({
    url : '{% url 'doctor_schedule' %}', // hardcoded
    method : 'POST',
    data : data,

    success : function(json) {
      console.log(json)
      console.log(fired_button)
      //location.reload();
      document.getElementById("currently-seeing").innerHTML = "Currently Seeing: " + fired_button;
    },

    error: function(xhr, errmsg, err) {
      console.log(xhr)
      console.log(errmsg)
    }
  });
};*/
/*function see_patient() {
  // TODO: confirm first
  var fired_button = $(this).val();
  $.ajax({
    url : 'see_patient/',
    type : "POST",
    data : { appointment_id: fired_button, },

    success : function(json) {
      console.log(json)
      console.log(fired_button)
    },

    error : function(xhr, errmsg, err) {
      console.log("an error occurs")
    }
  });
};*/
