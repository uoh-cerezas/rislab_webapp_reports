function validateContact(event) {
  event.preventDefault();

  const titleInput = document.getElementById("text-input");
  const emailInput = document.getElementById("email-input");
  const descriptionInput = document.getElementById("textarea-input");

  const missingFields = [];

  // Verificar cada campo obligatorio
  if (!titleInput || !titleInput.value.trim()) {
    missingFields.push("📝 Título");
  }
  if (!emailInput || !emailInput.value.trim()) {
    missingFields.push("📧 Email de contacto");
  }
  if (!descriptionInput || !descriptionInput.value.trim()) {
    missingFields.push("📄 Descripción");
  }

  // Validar formato de email si está presente
  if (
    emailInput &&
    emailInput.value.trim() &&
    !isValidEmail(emailInput.value.trim())
  ) {
    missingFields.push("📧 Ingresar email con formato válido");
  }

  // Verificiar si se muestra el modal
  if (missingFields.length > 0) {
    showErrorModal(missingFields);
  } else {
    showConfirmationModal();
  }
}
// Funcion para verificar el email con regex
/* retorna true o false */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Cuando falta algo en algun field
function showErrorModal(missingFields) {
  const missingFieldsList = document.getElementById("missingFieldsList");
  if (!missingFieldsList) {
    console.error("No se encontró el elemento missingFieldsList");
    alert(
      "Error: No se pudo mostrar el modal de error. Elemento missingFieldsList no encontrado."
    );
    return;
  }

  missingFieldsList.innerHTML = "";

  missingFields.forEach((field) => {
    const li = document.createElement("li");
    li.textContent = field;
    li.style.marginBottom = "8px";
    li.style.fontSize = "14px";
    missingFieldsList.appendChild(li);
  });

  missingFieldsList.style.maxWidth = "300px";
  missingFieldsList.style.margin = "0 auto";
  missingFieldsList.style.paddingLeft = "20px";
  missingFieldsList.style.listStyle = "disc";

  // Intentar usar Bootstrap nativo
  const modalElement = document.getElementById("modalError");
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
  return;
}

function showConfirmationModal() {
  const titleValue = document.getElementById("text-input").value.trim();
  const emailValue = document.getElementById("email-input").value.trim();
  const descriptionValue = document
    .getElementById("textarea-input")
    .value.trim();

  // Para una preview del modal(que no se muestre todo hasta 100 palabras)
  const descriptionPreview =
    descriptionValue.length > 100
      ? descriptionValue.substring(0, 100) + "..."
      : descriptionValue;

  const fileInput = document.getElementById("file-multiple-input");
  const hasFiles = fileInput && fileInput.files && fileInput.files.length > 0;
  const fileCount = hasFiles ? fileInput.files.length : 0;

  const message =
    '<div class="text-center">' +
    '<div class="mb-3"><strong>Se enviará el siguiente mensaje de contacto:</strong></div>' +
    '<div class="card">' +
    '<div class="card-body text-left">' +
    '<div class="mb-2"><strong>📝 Título:</strong><br><em>"' +
    titleValue +
    '"</em></div>' +
    '<div class="mb-2"><strong>📧 Email:</strong><br><em>' +
    emailValue +
    "</em></div>" +
    '<div class="mb-2"><strong>📄 Descripción:</strong><br><em>"' +
    descriptionPreview +
    '"</em></div>' +
    (hasFiles
      ? '<div class="mb-2"><strong>📎 Archivos adjuntos:</strong><br><em>' +
        fileCount +
        " archivo(s) seleccionado(s)</em></div>"
      : "") +
    "</div>" +
    "</div>" +
    '<div class="mt-3 text-muted">¿Confirmas el envío de este mensaje?</div>' +
    "</div>";

  const modalMessage = document.getElementById("modalSubmitMessage");
  if (modalMessage) {
    modalMessage.innerHTML = message;
  }

  const modalElement = document.getElementById("modalSubmit");
  if (modalElement) {
    modalElement.style.display = "block";
    modalElement.classList.add("show");
    document.body.classList.add("modal-open");
    return;
  }
}

function submitContact() {
  const modal = document.getElementById("modalSubmit");
  if (modal) {
    modal.style.display = "none";
    modal.classList.remove("show");
    document.body.classList.remove("modal-open");
  }

  const payload = {
    title: document.getElementById("text-input").value.trim(),
    email: document.getElementById("email-input").value.trim(),
    description: document.getElementById("textarea-input").value.trim(),
  };

  const endpoint = window.contactEndpoint || "/api/contacto";

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then(async (response) => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.message || "No se pudo enviar el mensaje.");
      }
      return data;
    })
    .then(() => {
      showSuccessMessage();
      resetForm();
    })
    .catch((error) => {
      showRequestError(error.message || "No se pudo enviar el mensaje.");
    });
}

// Mostrar loading msg (quiza usar en un futuro)
// function showLoadingState() {
//   const loadingModal =
//     '<div class="modal fade" id="modalLoading" tabindex="-1" role="dialog" data-backdrop="static" data-keyboard="false">' +
//     '<div class="modal-dialog modal-dialog-centered modal-sm" role="document">' +
//     '<div class="modal-content">' +
//     '<div class="modal-body text-center py-4">' +
//     '<div class="spinner-border text-primary mb-3" role="status">' +
//     '<span class="sr-only">Enviando...</span>' +
//     "</div>" +
//     "<div>Enviando mensaje...</div>" +
//     "</div>" +
//     "</div>" +
//     "</div>" +
//     "</div>";

//   if (!document.getElementById("modalLoading")) {
//     document.body.insertAdjacentHTML("beforeend", loadingModal);
//   }

//   const modal = document.getElementById("modalLoading");
//   if (modal) {
//     modal.style.display = "block";
//     modal.classList.add("show");
//     document.body.classList.add("modal-open");
//   }
// }

// Esconder loading msg (comentado quiza usar en un futuro)
// function hideLoadingState() {
//   const modal = document.getElementById("modalLoading");
//   if (modal) {
//     modal.style.display = "none";
//     modal.classList.remove("show");
//     document.body.classList.remove("modal-open");
//     // setTimeout(() => {
//     //   modal.remove();
//     // }, 500);
//   }
// }

function showSuccessMessage() {
  const successModal =
    '<div class="modal fade" id="modalSuccess" tabindex="-1" role="dialog">' +
    '<div class="modal-dialog modal-dialog-centered modal-md" role="document">' +
    '<div class="modal-content">' +
    '<div class="modal-header bg-success text-white">' +
    '<h4 class="modal-title">' +
    '<i class="ti-check mr-2"></i>¡Mensaje enviado correctamente!' +
    "</h4>" +
    '<button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">' +
    '<span aria-hidden="true">&times;</span>' +
    "</button>" +
    "</div>" +
    '<div class="modal-body text-center py-4">' +
    '<div class="mb-3">' +
    '<i class="ti-email" style="font-size: 48px; color: #28a745;"></i>' +
    "</div>" +
    '<p class="mb-3">Tu mensaje ha sido enviado exitosamente.</p>' +
    '<p class="text-muted">Te contactaremos pronto a través del email proporcionado.</p>' +
    "</div>" +
    '<div class="modal-footer">' +
    '<button type="button" class="btn btn-success" data-dismiss="modal">Perfecto</button>' +
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

    // setTimeout(() => {
    //   modal.style.display = "none";
    //   modal.classList.remove("show");
    //   document.body.classList.remove("modal-open");
    //   setTimeout(() => {
    //     modal.remove();
    //   }, 500);
    // }, 5000);
  }
}

function showRequestError(message) {
  const requestModal = document.getElementById("modalRequestError");
  const messageElement = document.getElementById("modalRequestErrorMessage");

  if (messageElement) {
    messageElement.textContent = message;
  }

  if (requestModal) {
    requestModal.style.display = "block";
    requestModal.classList.add("show");
    document.body.classList.add("modal-open");
  } else {
    alert(message);
  }
}

function resetForm() {
  document.getElementById("text-input").value = "";
  document.getElementById("email-input").value = "";
  document.getElementById("textarea-input").value = "";

  const fileInput = document.getElementById("file-multiple-input");
  if (fileInput) {
    fileInput.value = "";
  }
}

// Función de inicialización
function initializeContactForm() {
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
      }
    });
  });
}

// Inicializar cuando se carga el script
initializeContactForm();
