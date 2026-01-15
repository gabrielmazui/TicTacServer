// Overlay criar partida
const createServerBtn = document.getElementById("create-server");
const overlay = document.getElementById("overlay");
const closeOverlayBtn = document.getElementById("close-overlay");
const confirmCreateBtn = document.getElementById("confirm-create");

createServerBtn.addEventListener("click", () => overlay.style.display="flex");
closeOverlayBtn.addEventListener("click", () => overlay.style.display="none");
overlay.addEventListener("click", e => { if(e.target===overlay) overlay.style.display="none"; });

async function create_match() {
  const response = await fetch("/create-math", {
    method: "POST"
  });

  if (response.redirected) {
    window.location.href = response.url;
    return;
  }

  const data = await response.json();

  window.location.href = `/match/${data.match_id}`;
}

confirmCreateBtn.addEventListener("click", () => {
    overlay.style.display="none";
    create_match()
});

const logo = document.getElementById("logo")
logo.addEventListener("click", () =>{
  window.location.href = "/";
})

const userArea = document.getElementById("user-area");
const logoutBtn = document.getElementById("logout-btn");

// abre / fecha ao clicar no username
userArea.addEventListener("click", (e) => {
  e.stopPropagation(); // impede fechar imediatamente
  logoutBtn.classList.toggle("show");
});

// click fora fecha
document.addEventListener("click", () => {
  logoutBtn.classList.remove("show");
});

async function logout(){
  const response = await fetch("/logout", {
    method: "POST"
  });
  if (response.redirected) {
    window.location.href = response.url;
    return;
  }
}

// click no sair
logoutBtn.addEventListener("click", (e) => {
  e.stopPropagation(); // não fecha antes de executar
  logoutBtn.classList.remove("show");
  logout()
});


// Função para ouvir clicks nos matches
document.querySelectorAll(".join-btn").forEach(btn => {
  btn.addEventListener("click", () => {
      const matchId = btn.dataset.id;
      window.location.href = `/room/${matchId}`;
  });
});

document.querySelectorAll(".watch-btn").forEach(btn => {
  btn.addEventListener("click", () => {
      const matchId = btn.dataset.id;
      window.location.href = `/room/${matchId}`;
  });
});

const ws = new WebSocket("ws://localhost:8080/ws/session");

ws.onmessage = (event) => {
    if (event.data === "logout") {
        // recebeu evento de logout → redireciona pra login
        window.location.href = "/login";
    }
};

ws.onclose = (event) => {
    console.log("oi")
    window.location.href = "/login";
};