// JS para validar formulario de Porciones Frío con modales y envío AJAX

function validateChill(event) {
    event.preventDefault();

    const fieldSel = document.getElementById("select-field");
    const zoneSel = document.getElementById("select-zone");
    const fechaInicio = document.getElementById("fechaInicio");
    const fechaFin = document.getElementById("fechaFin");

    const missing = [];

    if (!fieldSel || !fieldSel.value || fieldSel.value === "0") {
        missing.push("Campo");
    }
    if (!zoneSel || !zoneSel.value || zoneSel.value === "0") {
        missing.push("Cuartel");
    }
    if (!fechaInicio || !fechaInicio.value) {
        missing.push("Fecha inicial");
    }
    if (!fechaFin || !fechaFin.value) {
        missing.push("Fecha final");
    }
    // Validación de rango
    if (fechaInicio && fechaFin && fechaInicio.value && fechaFin.value) {
        if (fechaFin.value < fechaInicio.value) {
            missing.push("Rango de fechas inválido (final < inicial)");
        }
    }

    if (missing.length > 0) {
        showErrorModal(missing);
        return false;
    }

    // Mostrar confirmación con resumen
    const fieldText = fieldSel.options[fieldSel.selectedIndex]?.text || fieldSel.value;
    const zoneText = zoneSel.options[zoneSel.selectedIndex]?.text || zoneSel.value;

    const summary = `
    <div class="text-center">
      <div class="mb-3">Se generará un reporte de porciones frío con:</n></div>
      <ul class="list-unstyled mx-auto text-left" style="max-width: 360px;">
        <li><strong>Campo:</strong> ${fieldText}</li>
        <li><strong>Cuartel:</strong> ${zoneText}</li>
        <li><strong>Fecha inicial:</strong> ${fechaInicio.value}</li>
        <li><strong>Fecha final:</strong> ${fechaFin.value}</li>
      </ul>
      <div class="mt-2">¿Deseas continuar?</div>
    </div>
  `;

    const modalMessage = document.getElementById("modalSubmitMessage");
    if (modalMessage) modalMessage.innerHTML = summary;

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

    return true;
}

function showErrorModal(missingList) {
    const ul = document.getElementById("missingFilesList");
    if (!ul) return;
    ul.innerHTML = "";
    missingList.forEach((label) => {
        const li = document.createElement("li");
        li.textContent = `• ${label}`;
        ul.appendChild(li);
    });
    ul.style.maxWidth = "320px";
    ul.style.margin = "0 auto";
    ul.style.paddingLeft = "0";
    ul.style.listStyle = "none";

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

function submitFiles() {
    // Reutilizamos el id del botón de confirmación existente
    const modalElement = document.getElementById("modalSubmit");
    if (modalElement) {
        modalElement.classList.remove("show");
        modalElement.style.display = "none";
        const backdrop = document.getElementById("submit-backdrop");
        if (backdrop) backdrop.remove();
    }
    document.body.classList.remove("modal-open");

    showLoadingModal();

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    fetch(form.action || window.location.href, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
    })
        .then((res) => {
            hideLoadingModal();
            if (res.ok) return res.json();
            throw new Error("Respuesta no válida del servidor");
        })
        .then((data) => {
            if (data && data.success) {
                showSuccessMessage();
            } else {
                showErrorMessage(data?.message || "No se pudo completar la solicitud.");
            }
        })
        .catch((err) => {
            hideLoadingModal();
            console.error(err);
            showErrorMessage("Error de conexión. Inténtalo nuevamente.");
        });
}

function showLoadingModal() {
    const html = `
  <div class="modal fade" id="modalLoading" tabindex="-1" role="dialog" data-backdrop="static" data-keyboard="false">
    <div class="modal-dialog modal-dialog-centered modal-sm" role="document">
      <div class="modal-content">
        <div class="modal-body text-center py-4">
          <div class="spinner-border text-primary mb-3" role="status">
            <span class="sr-only">Cargando...</span>
          </div>
          <p class="mb-0">Generando solicitud...</p>
        </div>
      </div>
    </div>
  </div>`;

    if (!document.getElementById("modalLoading")) {
        document.body.insertAdjacentHTML("beforeend", html);
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
    if (backdrop) backdrop.remove();
    document.body.classList.remove("modal-open");
}

function showSuccessMessage() {
    const html = `
  <div class="modal fade" id="modalSuccess" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered modal-md" role="document">
      <div class="modal-content">
        <div class="modal-header bg-success text-white">
          <h4 class="modal-title"><i class="ti-check mr-2"></i>Solicitud enviada</h4>
        </div>
        <div class="modal-body text-center py-4">
          <div class="mb-3"><i class="ti-check-box" style="font-size:48px;color:#28a745"></i></div>
          <p class="mb-0">Se registró la solicitud de reporte de porciones frío.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-success" onclick="redirectToService()">Continuar</button>
        </div>
      </div>
    </div>
  </div>`;

    if (!document.getElementById("modalSuccess")) {
        document.body.insertAdjacentHTML("beforeend", html);
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
    const html = `
  <div class="modal fade" id="modalUploadError" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered modal-md" role="document">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h4 class="modal-title"><i class="ti-alert mr-2"></i>Error</h4>
          <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body text-center py-4">
          <p class="mb-0">${message}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" data-dismiss="modal">Entendido</button>
        </div>
      </div>
    </div>
  </div>`;

    if (document.getElementById("modalUploadError")) {
        document.getElementById("modalUploadError").remove();
    }
    document.body.insertAdjacentHTML("beforeend", html);

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
    window.location.href = "/porciones_frio";
}

// Cierre genérico de modales/backdrops
(function initializeChillUpload() {
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
                const backdrops = document.querySelectorAll(".modal-backdrop");
                backdrops.forEach((bd) => bd.remove());
            }
        }
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            const visibleModals = document.querySelectorAll(".modal.show");
            visibleModals.forEach((m) => {
                m.style.display = "none";
                m.classList.remove("show");
            });
            const backdrops = document.querySelectorAll(".modal-backdrop");
            backdrops.forEach((bd) => bd.remove());
            document.body.classList.remove("modal-open");
        }
    });
})();
