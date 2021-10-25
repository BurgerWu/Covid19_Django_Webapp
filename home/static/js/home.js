// Detect submit button click and set a localStorage//
$('#feedback_submit_btn').click(function(){
 localStorage.setItem('form_submitted', 'form_submitted');
});

//  If the home page loaded with sign of feedback submission, open message modal to return message  //
$('document').ready(function(){
  var modalId = localStorage.getItem('form_submitted');
  if (modalId != null){
    $('#message_modal').modal("show");
    localStorage.removeItem('form_submitted');
  }
})