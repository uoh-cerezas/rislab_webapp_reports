export function checkDuplicatedUser(formId, inputData, errorMsgId, inputType) {
    document.getElementById(formId).addEventListener("submit", async function (e) {
        e.preventDefault(); // Bloquea el envío inicial

        const input = document.getElementById(inputData).value.trim();
        const mensajeError = document.getElementById(errorMsgId);
        
        if (input === "") {
            mensajeError.textContent = "Debe llenar todos los campos con datos válidos.";
            mensajeError.style.display = "block";
            return;
        }

        try {
            const respuesta = await fetch("/checkDuplicates", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ value : input})
            });

            const data = await respuesta.json();

            if (data === 0) { //  Case where is available to use
                mensajeError.style.display = "none";
                this.submit();
            } else if (data === 1) { // Case where is not available to use
                mensajeError.textContent = `El ${inputType} ingresado ya está en uso, elija otro por favor.`;
                mensajeError.style.display = "block";
            }
        } catch (err) {
            mensajeError.textContent = "Error de conexión. Intenta de nuevo.";
            mensajeError.style.display = "block";
        }
    });
}