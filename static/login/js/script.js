document.addEventListener("DOMContentLoaded", () => {

  const loginForm = document.getElementById("login-form");
  const loginBtn = document.getElementById("login-btn");
  const registerBtn = document.getElementById("register-btn");


  const messageBox = document.getElementById("form-message");

  const showMessage = (text, type = "error") => {
    messageBox.textContent = text;
    messageBox.className = `form-message ${type}`;
  };

  const hideMessage = () => {
    messageBox.className = "form-message hidden";
  };


  const lockUI = () => {
    loginBtn.disabled = true;
    registerBtn.disabled = true;
    document.body.classList.add("loading");
  };

  const unlockUI = () => {
    loginBtn.disabled = false;
    registerBtn.disabled = false;
    document.body.classList.remove("loading");
  };

  document.querySelectorAll("#username, #password").forEach(input => {
    input.addEventListener("input", hideMessage);
  });


  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    hideMessage();
    lockUI();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const keeplogged = document.getElementById("keeplogged").checked;

    if (!username || !password) {
      showMessage("Please fill in all fields.");
      unlockUI();
      return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    if (keeplogged) formData.append("keeplogged", "on");

    try {
      const res = await fetch("/login", {
        method: "POST",
        body: formData,
        credentials: "include",
        redirect: "follow" // default
      });

      if (res.redirected) {
        window.location.href = res.url;
        return;
      }

      if (!res.ok) {
        showMessage("Invalid username or password.");
        unlockUI();
      }

    } catch (err) {
      showMessage("Server unavailable. Try again later.");
      unlockUI();
    }
  });

  registerBtn.addEventListener("click", () => {
    lockUI();
    window.location.href = "/signup";
  });
});