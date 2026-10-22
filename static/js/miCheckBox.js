document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('checkBtnAddUser').addEventListener('click', function (event) {
        const checked = document.querySelectorAll('input[type="checkbox"]:checked').length;

        if (!checked) {
            alert('Debe marcar al menos 1 Servicio.');
            event.preventDefault(); // Previene comportamiento por defecto si es un botón de envío
            return false;
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('checkBtnModUser').addEventListener('click', function (event) {
        const checked = document.querySelectorAll('input[type="checkbox"]:checked').length;

        if (!checked) {
            alert('Debe marcar al menos 1 Servicio.');
            event.preventDefault(); // Previene comportamiento por defecto si es un botón de envío
            return false;
        }
    });
});