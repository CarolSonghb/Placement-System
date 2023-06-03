// Path: static/js/index.js
console.log('Hello World from group 25')
let year = document.getElementById('currentYear');
year.innerHTML = new Date().getFullYear(); // this makes the year change

// go back to previous page
 function goBack() {
   window.history.back();
 }

// function to show and hide password

// side bar expand
var arrow = document.querySelectorAll(".arrow");
for (var i = 0; i < arrow.length; i++) {
  arrow[i].addEventListener("click", function(e) {
    var arrowParent = e.target.parentElement.parentElement; //selecting main parent of arrow
    arrowParent.classList.toggle("showMenu");
  });
}
var sidebar = document.querySelector(".sidebar");
var sidebarBtn = document.querySelector(".bx-menu");
console.log(sidebarBtn);
sidebarBtn.addEventListener("click", function() {
  sidebar.classList.toggle("close");
});



var btn5 = document.getElementById('project_update');
var form5 = document.getElementById('mentorproject');

  btn5.onclick = function(event) {
    event.preventDefault();

    xtalert.alertConfirm({
      "confirmText":"Confirm",
      "cancelText":"Cancel",
      "msg": "Do you want to update current Project?",
      "confirmCallback": function(){
        form5.submit();
      },
      "cancelCallback": function(){
      }
    });
  };



