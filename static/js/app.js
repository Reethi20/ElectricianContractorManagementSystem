function handleLogin(event) {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if (!email || !password) {
        alert("All fields are required");
        event.preventDefault();
    }
}

function handleRegister(event) {
    let phone = document.getElementById("phone").value;

    if (phone.length !== 10) {
        alert("Phone must be 10 digits");
        event.preventDefault();
    }
}