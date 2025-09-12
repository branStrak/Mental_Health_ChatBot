

const goToIndexBtn = document.getElementById('go-to-index');
if (goToIndexBtn) {
  goToIndexBtn.addEventListener('click', () => {
    window.location.href = '/index';
  });
}

window.addEventListener('load', function() {
const isAllowed = localStorage.getItem('isLoggedIn');

if (isAllowed === 'true') {
  document.getElementById('sign-out-btn').style.display = 'inline-block';
  document.getElementById('sign-in-btn').style.display = 'none';

  document.querySelector('.sign-up-btn').style.display = 'none';


} else {
  console.log('Form will not be shown. LocalStorage value is not "true".');
}
});


const signInBtn = document.getElementById('sign-in-btn');
  const signUpBtn = document.querySelector('.sign-up-btn');
  const signOutBtn = document.getElementById('sign-out-btn');
const modal = document.getElementById('profile-modal');
const profileBtn = document.getElementById('profile-btn');
const closeBtn = document.querySelector('.close-btn');
const editBtn = document.getElementById('edit-btn');
const deleteBtn = document.getElementById('delete-btn');

const inputs = document.querySelectorAll('#profile-form input');

const userId = localStorage.getItem("userId"); // Assuming user ID is stored

function fetchUserInfo() {

if (!userId) {
console.error("User ID not found in localStorage.");

} else {
fetch(`/get_user_info/${userId}`)
.then(res => res.json())
.then(data => {
document.getElementById('username').value = data.username;
document.getElementById('email').value = data.email;
document.getElementById('password').value = "";
})
.catch(err => {
console.error("Error fetching user info:", err);
});
}
}
profileBtn.addEventListener('click', () => {
  updateprofilevalue();
modal.style.display = 'flex';
const th=localStorage.getItem("theme");
if(th==="dark"){
  document.getElementById("content").style.backgroundColor="white";
  document.getElementById("pfp").style.color  ="Black";

}

fetchUserInfo();
});  closeBtn.addEventListener('click', () => modal.style.display = 'none');

let isEditable = false;
editBtn.addEventListener('click', () => {
isEditable = !isEditable;
inputs.forEach(input => input.disabled = !isEditable);
editBtn.textContent = isEditable ? 'Save' : 'Update';

if (!isEditable) {
// Placeholder for update logic (e.g., send to backend via fetch)
const updatedData = {
  username: document.getElementById('username').value,
  email: document.getElementById('email').value,
  password: document.getElementById('password').value
};

fetch(`/update_user_info/${userId}`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(updatedData)
}).then(res => res.json())
  .then(result => {
    if (result.success) {
      alert("User info updated successfully.");
    }
  });
console.log('Send to backend:', updatedData);
// Add your fetch() here to POST data to Flask
}
});


deleteBtn.addEventListener('click',()=>{
  fetch(`/delete_user/${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  }).then(res => res.json())
    .then(result => {
      if (result.success) {
        
        alert(result.message);
      }
    });
    localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('userId');
        updateAuthButtons();
        updateprofilevalue();

        
});

function updateAuthButtons() {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  
    if (isLoggedIn) {
      if (signInBtn) signInBtn.style.display = 'none';
      if (signUpBtn) signUpBtn.style.display = 'none';
      if (themeToggleBtn) themeToggleBtn.style.display = 'inline-block';
      if (signOutBtn) signOutBtn.style.display = 'inline-block';
      if (signOutBtn1) signOutBtn.style.display = 'inline-block';


    } else {
      if (signInBtn) signInBtn.style.display = 'inline-block';
      if (signUpBtn) signUpBtn.style.display = 'inline-block';
      if (signOutBtn) signOutBtn.style.display = 'none';

    }
  
}
function updateprofilevalue(){
  if(localStorage.getItem('isLoggedIn')){

    document.getElementById('username').value="user";
    document.getElementById('email').value="user@gmail.com";
    document.getElementById('password').value="";
  }
  }






// Optional: close modal on click outside
window.addEventListener('click', (e) => {
if (e.target === modal) modal.style.display = 'none';
});



