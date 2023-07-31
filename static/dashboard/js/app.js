// // function set_class(id){
// //   document.getElementById(id).className += " active";
// // }
// document.getElementById("first").addEventListener("click", function() {
//   document.getElementById("first").classList.add('active');
//   $(".sidebar").on("click", function(e) {
//         e.preventDefault();
//         $("body").toggleClass("sb-sidenav-toggled");
//     });
// });
function menuToggle(){
  const togglemenu = document.querySelector('.menu');
  togglemenu.classList.toggle('active');
}
