function see_patient(appointment_id) {
  var fired_button = appointment_id
  document.getElementById("currently-seeing").innerHTML = "Currently Seeing: " + fired_button;
  
}
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
