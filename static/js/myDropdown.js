document.addEventListener("DOMContentLoaded", function () {
    var selects = document.querySelectorAll(".standardSelect");

    selects.forEach(function (select) {
    new Choices(select, {
        searchEnabled: true,
        noResultsText: "Oops, nothing found!",
        shouldSort: false,
    });

    // Agregar un listener para el cambio de selección
    // select.addEventListener('change', function() {
    //     // Comprobar si la primera opción está seleccionada (indice 0)
    //     if (select.selectedIndex === 0) {
    //     select.setCustomValidity("Por favor, selecciona una opción diferente de la primera.");
    //     } else {
    //     select.setCustomValidity(""); // Limpiar el mensaje de error
    //     }
    // });

    // // Asegurarse de que el select no tenga la opción predeterminada al enviar el formulario
    // select.form.addEventListener('submit', function(event) {
    //     if (select.selectedIndex === 0) {
    //     event.preventDefault(); // Evitar que el formulario se envíe
    //     alert("Por favor, selecciona una opción diferente de la primera.");
    //     }
    // });
    });
});