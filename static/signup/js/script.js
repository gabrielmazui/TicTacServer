document.addEventListener("DOMContentLoaded", () => {

    const signupForm = document.getElementById("signup-form");
    const signupBtn = document.getElementById("signup-btn");
    const loginBtn = document.getElementById("login-btn");
    const messageBox = document.getElementById("form-message");
    const passwordInput = document.getElementById("password");

    const lockUI = () => {
        signupBtn.disabled = true;
        loginBtn.disabled = true;
        document.body.classList.add("loading");
    };

    const unlockUI = () => {
        signupBtn.disabled = false;
        loginBtn.disabled = false;
        document.body.classList.remove("loading");
    };

    const showMessage = (text, type = "error") => {
        messageBox.textContent = text;
        messageBox.className = `form-message ${type}`;
    };

    const hideMessage = () => {
        messageBox.className = "form-message hidden";
    };

   
    const validateForm = () => {
        const username = document.getElementById("username").value.trim();
        const password = passwordInput.value;

        let errors = [];

        if (username.length < 3) errors.push("Username must be at least 3 characters");
        if (password.length < 6) errors.push("Password must be at least 6 characters");

        if (errors.length > 0) {
            showMessage(errors[0]);
            signupBtn.disabled = true;
            return false;
        }

        hideMessage();
        signupBtn.disabled = false;
        return true;
    };

    
    document.querySelectorAll("#username, #password").forEach(input => {
        input.addEventListener("input", validateForm);
    });

   
    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!validateForm()) return;

        lockUI();

        const username = document.getElementById("username").value.trim();
        const password = passwordInput.value.trim();

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        try {
            const res = await fetch("/signup", {
                method: "POST",
                body: formData,
                credentials: "include",
                redirect: "follow" // default
            });
            
            if (res.redirected) {
                window.location.href = res.url;
                return;
            }

            // Erros específicos
            if (res.status === 400) {
                showMessage("Username already exists");
                unlockUI(); 
            } else if (res.status === 422) {
                showMessage("Invalid data (password too short or invalid)");
                unlockUI(); 
            } else if (!res.ok) {
                showMessage("Unexpected error occurred");
                unlockUI(); 
            }

        } catch(err) {
            showMessage("Server unavailable. Please try again later.");
            unlockUI(); 
        }
    });

    
    loginBtn.addEventListener("click", () => {
        window.location.href = "/login";  
    });

});