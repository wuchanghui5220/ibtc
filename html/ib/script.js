var modal = document.getElementById("myModal");
var img = document.getElementById("myImg");
var modalImg = document.getElementById("img01");
var span = document.getElementsByClassName("close")[0];

img.onclick = function(){
  modal.style.display = "block";
  modalImg.src = this.src;
}

span.onclick = function() { 
  modal.style.display = "none";
}

modal.onclick = function() {
  modal.style.display = "none";
}
