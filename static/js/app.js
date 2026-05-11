function handleLogin(event){

    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();

    if(email === "" || password === ""){

        alert("Please fill all fields");
        event.preventDefault();

    }

}

function handleRegister(event){

    let name = document.getElementById("name").value.trim();
    let phone = document.getElementById("phone").value.trim();
    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();

    if(name === "" || phone === "" || email === "" || password === ""){

        alert("All fields are required");
        event.preventDefault();
        return;

    }

    if(phone.length !== 10 || isNaN(phone)){

        alert("Phone number must contain 10 digits");
        event.preventDefault();
        return;

    }

    if(password.length < 8){

        alert("Password must contain at least 8 characters");
        event.preventDefault();

    }

}