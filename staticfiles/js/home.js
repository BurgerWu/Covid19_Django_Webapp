// $('#feedback_submit_btn').click(function(){
//     $('#feedbackmodal').modal('hide');
//     $('document').ready(function(){
//       $('#message_modal').modal('show');  
//     })    
//  });
$('#feedback_submit_btn').click(function(){
 localStorage.setItem('form_submitted', 'form_submitted');
});

$('document').ready(function(){
  var modalId = localStorage.getItem('form_submitted');
  if (modalId != null){
    $('#message_modal').modal("show");
    localStorage.removeItem('form_submitted');
  }
})