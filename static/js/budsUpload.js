// Validación de archivos con modales personalizados para Buds Count

function validateFiles(event) {
    event.preventDefault();

    const file1 = document.getElementById("file1");
    const file2 = document.getElementById("file2");
    const file3 = document.getElementById("file3");
    
    // Campos del formulario
    const selectField = document.getElementById("select-field");
    const selectZone = document.getElementById("select-zone");
    const selectType = document.getElementById("select-type-file");
    const selectExtension = document.getElementById("select-extension-file");
    const textDiaDatos = document.getElementById("text-dia-datos");
    const textNumArboles = document.getElementById("text-num-arboles");

    const missingFields = [];

    // Verificar cada archivo
    if (!file1.files || file1.files.length === 0) {
        missingFields.push("📹 Archivo comprimido (Videos)");
    }
    if (!file2.files || file2.files.length === 0) {
        missingFields.push("📋 Registro (Nombres de archivos)");
    }
    if (!file3.files || file3.files.length === 0) {
        missingFields.push("📊 Conteo");
    }
    
    // Verificar campos adicionales
    if (!selectField || !selectField.value || selectField.value === "0") {
        missingFields.push("- Campo");
    }
    if (!selectZone || !selectZone.value || selectZone.value === "0") {
        missingFields.push("- Cuartel");
    }
    if (!selectType || !selectType.value || selectType.value === "0") {
        missingFields.push("- Tipo");
    }
    if (!selectExtension || !selectExtension.value || selectExtension.value === "0") {
        missingFields.push("- Extensión");
    }
    if (!textDiaDatos || !textDiaDatos.value) {
        missingFields.push("- Día de toma de datos");
    }
    if (!textNumArboles || !textNumArboles.value) {
        missingFields.push("- Número Árboles");
        // ver si es un número válido, no float
    } else if (isNaN(textNumArboles.value) || parseInt(textNumArboles.value) <= 0 || !Number.isInteger(Number(textNumArboles.value))) {
        missingFields.push("- Número Árboles debe ser mayor a 0 y entero!");
    }

    if (missingFields.length > 0) {
        // Mostrar modal de error
        showErrorModal(missingFields);
    } else {
        // Mostrar modal de confirmación
        showConfirmationModal();
    }
}

// Función para mostrar el modal de error
function showErrorModal(missingFiles) {
    const missingFilesList = document.getElementById("missingFilesList");
    if (!missingFilesList) {
        console.error("No se encontró el elemento missingFilesList");
        return;
    }

    missingFilesList.innerHTML = "";

    missingFiles.forEach((file) => {
        const li = document.createElement("li");
        li.textContent = file;
        li.style.marginBottom = "8px";
        missingFilesList.appendChild(li);
    });

    // CENTRAR Y LIMITAR ANCHO
    missingFilesList.style.maxWidth = "350px";
    missingFilesList.style.margin = "0 auto";
    missingFilesList.style.paddingLeft = "0";
    missingFilesList.style.listStyle = "none";

    const modalElement = document.getElementById("modalError");
    if (modalElement) {
        modalElement.classList.add("show");
        modalElement.style.display = "block";
        modalElement.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");

        const backdrop = document.createElement("div");
        backdrop.className = "modal-backdrop fade show";
        backdrop.id = "error-backdrop";
        document.body.appendChild(backdrop);
    }
}

function showConfirmationModal() {
    const file1Name = document.getElementById("file1").files[0]?.name || "";
    const file2Name = document.getElementById("file2").files[0]?.name || "";
    const file3Name = document.getElementById("file3").files[0]?.name || "";
    
    const fieldSel = document.getElementById("select-field");
    const zoneSel = document.getElementById("select-zone");
    const typeSel = document.getElementById("select-type-file");
    const extensionSel = document.getElementById("select-extension-file");
    const diaDatos = document.getElementById("text-dia-datos").value;
    const numArboles = document.getElementById("text-num-arboles").value;
    
    const fieldText = fieldSel.options[fieldSel.selectedIndex]?.text || fieldSel.value;
    const zoneText = zoneSel.options[zoneSel.selectedIndex]?.text || zoneSel.value;
    const typeText = typeSel.options[typeSel.selectedIndex]?.text || typeSel.value;
    const extensionText = extensionSel.options[extensionSel.selectedIndex]?.text || extensionSel.value;

    const message = `
    <div class="text-center">
        <div class="mb-3"><strong>Resumen de información del reporte:</strong></div>
        <ul class="list-unstyled mx-auto text-left" style="max-width: 400px;">
        <li><strong>📹 Archivo comprimido:</strong> ${file1Name}</li>
        <li><strong>📋 Registro:</strong> ${file2Name}</li>
        <li><strong>📊 Conteo:</strong> ${file3Name}</li>
        <li><strong>- Campo:</strong> ${fieldText}</li>
        <li><strong>- Cuartel:</strong> ${zoneText}</li>
        <li><strong>- Tipo:</strong> ${typeText}</li>
        <li><strong>- Extensión:</strong> ${extensionText}</li>
        <li><strong>- Día de toma de datos:</strong> ${diaDatos}</li>
        <li><strong>- Número Árboles:</strong> ${numArboles}</li>
        </ul>
        <div class="mt-3">¿Deseas generar el reporte con esta información?</div>
    </div>
    `;

    const modalMessage = document.getElementById("modalSubmitMessage");
    if (modalMessage) {
        modalMessage.innerHTML = message;
    }

    const modalElement = document.getElementById("modalSubmit");
    if (modalElement) {
        modalElement.classList.add("show");
        modalElement.style.display = "block";
        modalElement.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");

        const backdrop = document.createElement("div");
        backdrop.className = "modal-backdrop fade show";
        backdrop.id = "submit-backdrop";
        document.body.appendChild(backdrop);
    }
}

function submitFiles() {
    // Cerrar modal de confirmación
    const modalElement = document.getElementById("modalSubmit");
    if (modalElement) {
        modalElement.classList.remove("show");
        modalElement.style.display = "none";

        const backdrop = document.getElementById("submit-backdrop");
        if (backdrop) {
            backdrop.remove();
        }
    }

    document.body.classList.remove("modal-open");

    // Mostrar modal de carga
    showLoadingModal();

    // Enviar el formulario mediante AJAX para controlar la redirección
    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    fetch(form.action || window.location.href, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
    })
        .then((response) => {
            hideLoadingModal();
            if (response.ok) {
                showSuccessMessage();
            } else {
                showErrorMessage("Error al enviar los archivos. Intenta nuevamente.");
            }
        })
        .catch((error) => {
            hideLoadingModal();
            showErrorMessage("Error de conexión. Verifica tu red e intenta nuevamente.");
            console.error("Error:", error);
        });
}

function showLoadingModal() {
    const loadingModal =
        '<div class="modal fade" id="modalLoading" tabindex="-1" role="dialog" data-backdrop="static" data-keyboard="false">' +
        '<div class="modal-dialog modal-dialog-centered modal-sm" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-body text-center py-4">' +
        '<div class="spinner-border text-primary mb-3" role="status">' +
        '<span class="sr-only">Cargando...</span>' +
        "</div>" +
        '<p class="mb-2">Subiendo archivos grandes...</p>' +
        '<p class="text-muted" style="font-size: 0.9rem;">Este proceso puede tardar varios minutos. Por favor, no cierre ni recargue la página.</p>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>";

    if (!document.getElementById("modalLoading")) {
        document.body.insertAdjacentHTML("beforeend", loadingModal);
    }

    const modal = document.getElementById("modalLoading");
    if (modal) {
        modal.style.display = "block";
        modal.classList.add("show");
        document.body.classList.add("modal-open");

        const backdrop = document.createElement("div");
        backdrop.className = "modal-backdrop fade show";
        backdrop.id = "loading-backdrop";
        document.body.appendChild(backdrop);
    }
}

function hideLoadingModal() {
    const modal = document.getElementById("modalLoading");
    if (modal) {
        modal.style.display = "none";
        modal.classList.remove("show");
    }

    const backdrop = document.getElementById("loading-backdrop");
    if (backdrop) {
        backdrop.remove();
    }

    document.body.classList.remove("modal-open");
}

function showSuccessMessage() {
    const successModal =
        '<div class="modal fade" id="modalSuccess" tabindex="-1" role="dialog">' +
        '<div class="modal-dialog modal-dialog-centered modal-md" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-header bg-success text-white">' +
        '<h4 class="modal-title">' +
        '<i class="ti-check mr-2"></i>¡Archivos enviados correctamente!' +
        "</h4>" +
        "</div>" +
        '<div class="modal-body text-center py-4">' +
        '<div class="mb-3">' +
        '<i class="ti-check-circle" style="font-size: 48px; color: #28a745;"></i>' +
        "</div>" +
        '<p class="mb-3">Tus archivos han sido enviados exitosamente.</p>' +
        '<p class="text-muted">Pronto se generará el reporte correspondiente.</p>' +
        "</div>" +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-success" onclick="redirectToService()">Continuar</button>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>";

    if (!document.getElementById("modalSuccess")) {
        document.body.insertAdjacentHTML("beforeend", successModal);
    }

    const modal = document.getElementById("modalSuccess");
    if (modal) {
        modal.style.display = "block";
        modal.classList.add("show");
        document.body.classList.add("modal-open");

        const backdrop = document.createElement("div");
        backdrop.className = "modal-backdrop fade show";
        backdrop.id = "success-backdrop";
        document.body.appendChild(backdrop);
    }
}

function showErrorMessage(message) {
    const errorModal =
        '<div class="modal fade" id="modalUploadError" tabindex="-1" role="dialog">' +
        '<div class="modal-dialog modal-dialog-centered modal-md" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-header bg-danger text-white">' +
        '<h4 class="modal-title">' +
        '<i class="ti-alert mr-2"></i>Error en el envío' +
        "</h4>" +
        '<button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        "</button>" +
        "</div>" +
        '<div class="modal-body text-center py-4">' +
        `
<p class="mb-0">${message}</p>
` +
        "</div>" +
        '<div class="modal-footer">' +
        '<button type="button" class="btn btn-primary" data-dismiss="modal">Entendido</button>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>";

    if (document.getElementById("modalUploadError")) {
        document.getElementById("modalUploadError").remove();
    }

    document.body.insertAdjacentHTML("beforeend", errorModal);

    const modal = document.getElementById("modalUploadError");
    if (modal) {
        modal.style.display = "block";
        modal.classList.add("show");
        document.body.classList.add("modal-open");

        const backdrop = document.createElement("div");
        backdrop.className = "modal-backdrop fade show";
        backdrop.id = "upload-error-backdrop";
        document.body.appendChild(backdrop);
    }
}

function redirectToService() {
    // Redirigir a la página del servicio de Buds
    window.location.href = "/conteo_dardos";
}

function resetFiles() {
    document.getElementById("file1").value = "";
    document.getElementById("file2").value = "";
    document.getElementById("file3").value = "";

    // Para que no se queden los nombres puestos
    const fileDisplays = [
        "filename1", // Display para file1 (Videos)
        "filename2", // Display para file2 (Nombres)
        "filename3", // Display para file3 (Conteo)
    ];

    fileDisplays.forEach((displayId) => {
        const displayElement = document.getElementById(displayId);
        if (displayElement) {
            displayElement.textContent = "";
            displayElement.innerHTML = "";
        }
    });

    // Para cambiar el color (de verde a azul)
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach((input) => {
        // Disparar evento change para limpiar cualquier display asociado
        const event = new Event("change", { bubbles: true });
        input.dispatchEvent(event);
    });
}

// Manejo de eventos para cerrar modales
function initializeFilesUpload() {
    document.addEventListener("DOMContentLoaded", function () {
        // Manejar clicks en botones de cerrar modal
        document.addEventListener("click", function (e) {
            if (
                e.target.matches('[data-dismiss="modal"]') ||
                e.target.closest('[data-dismiss="modal"]')
            ) {
                const modal = e.target.closest(".modal");
                if (modal) {
                    modal.style.display = "none";
                    modal.classList.remove("show");
                    document.body.classList.remove("modal-open");

                    // Remover backdrops
                    const backdrops = document.querySelectorAll(".modal-backdrop");
                    backdrops.forEach((backdrop) => backdrop.remove());
                }
            }
        });

        // Cerrar modal al hacer click fuera
        document.addEventListener("click", function (e) {
            if (
                e.target.classList.contains("modal") &&
                !e.target.id.includes("modalLoading")
            ) {
                e.target.style.display = "none";
                e.target.classList.remove("show");
                document.body.classList.remove("modal-open");

                // Remover backdrops
                const backdrops = document.querySelectorAll(".modal-backdrop");
                backdrops.forEach((backdrop) => backdrop.remove());
            }
        });

        // Manejar tecla Escape
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                const visibleModals = document.querySelectorAll(
                    ".modal.show:not(#modalLoading)"
                );
                visibleModals.forEach(function (modal) {
                    modal.style.display = "none";
                    modal.classList.remove("show");
                    document.body.classList.remove("modal-open");
                });

                // Remover backdrops
                const backdrops = document.querySelectorAll(".modal-backdrop");
                backdrops.forEach((backdrop) => backdrop.remove());
            }
        });
    });
}

initializeFilesUpload();
