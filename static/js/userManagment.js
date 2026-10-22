document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("addUser");
  const serviceCheckboxes = document.querySelectorAll(".service-checkbox");
  const errorMessage = document.getElementById("serviceError");

  // Validar al enviar el formulario
  form.addEventListener("submit", function (event) {
    const isChecked = Array.from(serviceCheckboxes).some(
      (checkbox) => checkbox.checked
    );

    if (!isChecked) {
      event.preventDefault();
      errorMessage.classList.remove("d-none");
      serviceCheckboxes[0].focus();
      return false;
    }

    errorMessage.classList.add("d-none");
    return true;
  });

  // Ocultar error cuando se selecciona una opción
  serviceCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const isChecked = Array.from(serviceCheckboxes).some((cb) => cb.checked);
      if (isChecked) {
        errorMessage.classList.add("d-none");
      }
    });
  });
});
