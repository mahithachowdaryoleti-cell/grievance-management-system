document.getElementById("loginForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const role = document.getElementById("role").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const error = document.getElementById("error");

    if (role === "" || username === "" || password === "") {
        error.textContent = "All fields are required!";
        return;
    }

    // Dummy login logic (for project demo)
    if (password === "password123") {
        if (role === "student") {
            alert("Student Login Successful");
            // window.location.href = "student_dashboard.html";
        } 
        else if (role === "authority") {
            alert("Authority Login Successful");
            // window.location.href = "authority_dashboard.html";
        } 
        else if (role === "admin") {
            alert("Admin Login Successful");
            // window.location.href = "admin_dashboard.html";
        }
    } else {
        error.textContent = "Invalid username or password!";
    }
});
