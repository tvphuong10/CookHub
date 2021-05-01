document.getElementById('button').addEventListener('click',
function(event){
  event.preventDefault()
  document.querySelector('.bg-modal').style.display='flex';
});

document.querySelector('.close').addEventListener('click',
function(){
  document.querySelector('.bg-modal').style.display = 'none';
});



document.getElementById('button1').addEventListener('click',
function(event){
  event.preventDefault()
  document.querySelector('.bg-modal1').style.display='flex';
});

document.querySelector('.close1').addEventListener('click',
function(){
  document.querySelector('.bg-modal1').style.display = 'none';
});