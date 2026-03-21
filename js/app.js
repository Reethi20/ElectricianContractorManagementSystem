
// ================= LOGIN =================
function handleLogin(event){
    event.preventDefault();

    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if(email === "" || password === ""){
        alert("All fields are required!");
        return;
    }

    if(password.length < 6){
        alert("Password must be at least 6 characters");
        return;
    }

    // Store user in localStorage
    localStorage.setItem("userEmail", email);

    alert("Login Successful!");
    window.location.href = "dashboard.html";
}

// ================= REGISTER =================
function handleRegister(event){
    event.preventDefault();

    let name = document.getElementById("name").value;
    let phone = document.getElementById("phone").value;
    let email = document.getElementById("email").value;
    let role = document.getElementById("role").value;
    let password = document.getElementById("password").value;

    if(!name || !phone || !email || !role || !password){
        alert("All fields are required!");
        return;
    }

    if(phone.length !== 10){
        alert("Phone must be 10 digits");
        return;
    }

    if(password.length < 6){
        alert("Password must be at least 6 characters");
        return;
    }

    // Save user data
    localStorage.setItem("userName", name);
    localStorage.setItem("userEmail", email);

    alert("Registration Successful!");
    window.location.href = "login.html";
}

// ================= PROFILE LOAD =================
function loadProfile(){
    let name = localStorage.getItem("userName") || "Admin User";
    let email = localStorage.getItem("userEmail") || "admin@email.com";

    let nameEl = document.getElementById("profileName");
    let emailEl = document.getElementById("profileEmail");

    if(nameEl) nameEl.innerText = name;
    if(emailEl) emailEl.innerText = email;
}

// ================= LOGOUT =================
function logout(){
    localStorage.clear();
    alert("Logged out successfully");
    window.location.href = "login.html";
}

// ================= INIT =================
document.addEventListener("DOMContentLoaded", function(){
    loadProfile();
});