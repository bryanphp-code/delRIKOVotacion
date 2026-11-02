document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api";

    // Elementos del DOM
    const contestStatusBadge = document.getElementById("contest-status-badge");
    const closedAlert = document.getElementById("closed-alert");
    const viewRegister = document.getElementById("view-register");
    const viewVoting = document.getElementById("view-voting");
    const viewSuccess = document.getElementById("view-success");
    const formRegister = document.getElementById("form-register");
    const clientNameDisplay = document.getElementById("client-name-display");
    const participantsContainer = document.getElementById("participants-container");
    const btnLogout = document.getElementById("btn-logout");

    // Verificar si ya hay un cliente guardado en la sesión del navegador
    let currentClient = JSON.parse(localStorage.getItem("spa_client")) || null;

    // 1. Comprobar si el concurso está abierto o cerrado
    async function checkContestStatus() {
        try {
            const res = await fetch(`${API_URL}/admin/settings`);
            const settings = await res.json();
            
            if (settings.is_open) {
                contestStatusBadge.textContent = "¡Concurso Abierto! 🟢";
                contestStatusBadge.className = "badge bg-success";
                closedAlert.classList.add("d-none");
                evaluateViewState();
            } else {
                contestStatusBadge.textContent = "Votaciones Cerradas 🔴";
                contestStatusBadge.className = "badge bg-danger";
                closedAlert.classList.remove("d-none");
                viewRegister.classList.add("d-none");
                viewVoting.classList.add("d-none");
                viewSuccess.classList.add("d-none");
            }
        } catch (err) {
            console.error("Error al verificar estado del concurso:", err);
        }
    }

    // 2. Gestionar qué vista mostrar según el estado del cliente
    function evaluateViewState() {
        if (currentClient) {
            viewRegister.classList.add("d-none");
            viewSuccess.classList.add("d-none");
            viewVoting.classList.remove("d-none");
            clientNameDisplay.textContent = currentClient.full_name;
            loadParticipants();
        } else {
            viewRegister.classList.remove("d-none");
            viewVoting.classList.add("d-none");
            viewSuccess.classList.add("d-none");
        }
    }

    // 3. Registrar o identificar al cliente
    formRegister.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fullName = document.getElementById("full_name").value.trim();
        const documentNumber = document.getElementById("document_number").value.trim();
        const email = document.getElementById("email").value.trim();

        try {
            const res = await fetch(`${API_URL}/clients/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    full_name: fullName,
                    document_number: documentNumber,
                    phone: "",
                    email: email || null
                })
            });

            if (res.status === 409) {
                const err = await res.json();
                alert(err.detail || "Este documento ya votó.");
                return;
            }
            if (!res.ok) throw new Error("Error al registrar cliente");

            const client = await res.json();
            currentClient = client;
            localStorage.setItem("spa_client", JSON.stringify(client));
            evaluateViewState();
        } catch (err) {
            alert("Hubo un error al registrar tus datos. Inténtalo de nuevo.");
            console.error(err);
        }
    });

    // 4. Cargar la galería de participantes
    async function loadParticipants() {
        try {
            const res = await fetch(`${API_URL}/participants/`);
            const participants = await res.json();

            participantsContainer.innerHTML = "";
            if (participants.length === 0) {
                participantsContainer.innerHTML = `<div class="col-12 text-center text-muted"><p>No hay participantes registrados todavía.</p></div>`;
                return;
            }

            participants.forEach(p => {
                const col = document.createElement("div");
                col.className = "col";
                const photo = p.photo_url || "https://images.unsplash.com/photo-1509557965875-b88c97052f0e?auto=format&fit=crop&w=600&q=80";
                col.innerHTML = `
                    <div class="card h-100 shadow-sm border-0 rounded-4 overflow-hidden">
                        <img src="${photo}" class="card-img-top object-fit-cover" style="height: 220px;" alt="${p.full_name}">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title fw-bold text-dark">${p.full_name}</h5>
                            <p class="card-text text-muted small flex-grow-1">${p.description || "Sin descripción proporcionada."}</p>
                            <button class="btn btn-dark w-100 rounded-pill mt-3 btn-vote" data-id="${p.id}">
                                <i class="bi bi-star-fill text-warning"></i> Votar por este disfraz
                            </button>
                        </div>
                    </div>
                `;
                participantsContainer.appendChild(col);
            });

            // Asignar eventos a los botones de votación
            document.querySelectorAll(".btn-vote").forEach(btn => {
                btn.addEventListener("click", () => {
                    const participantId = parseInt(btn.getAttribute("data-id"));
                    castVote(participantId);
                });
            });

        } catch (err) {
            console.error("Error al cargar participantes:", err);
        }
    }

    // Cierra la sesión del cliente y muestra la pantalla de éxito
    function finishSession() {
        localStorage.removeItem("spa_client");
        currentClient = null;
        formRegister.reset();
        viewRegister.classList.add("d-none");
        viewVoting.classList.add("d-none");
        viewSuccess.classList.remove("d-none");
    }

    // 5. Emitir el voto
    async function castVote(participantId) {
        if (!confirm("¿Estás seguro de emitir tu voto por este participante? Esta acción es definitiva y no se puede cambiar.")) return;

        try {
            const res = await fetch(`${API_URL}/votes/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    client_id: currentClient.id,
                    participant_id: participantId
                })
            });

            const data = await res.json();

            if (!res.ok) {
                alert(data.detail || "No se pudo registrar el voto.");
                if (res.status === 400 && /ya ha emitido/i.test(data.detail || "")) {
                    finishSession();
                }
                return;
            }

            finishSession();

        } catch (err) {
            alert("Error de conexión al emitir el voto.");
            console.error(err);
        }
    }

    // 6. Cerrar sesión del cliente actual
    btnLogout.addEventListener("click", () => {
        localStorage.removeItem("spa_client");
        currentClient = null;
        formRegister.reset();
        evaluateViewState();
    });

    // Inicializar app
    checkContestStatus();
});