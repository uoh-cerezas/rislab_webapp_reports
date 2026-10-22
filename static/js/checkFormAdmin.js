export function checkDuplicated(formId,inputData,errorMsgId,inputType,adminEmailInput,adminPasswordInput) {
    const form = document.getElementById(formId);
    const errorMsgBlock = document.getElementById(errorMsgId);

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); 

        const user = document.getElementById(inputData).value.trim();
        const adminEmail = document.getElementById(adminEmailInput).value.trim();
        const adminPassword = document.getElementById(adminPasswordInput).value.trim();

        if (!user || !adminEmail || !adminPassword) {
            errorMsgBlock.textContent = "Debe llenar todos los campos con datos válidos.";
            errorMsgBlock.style.display = "block";
            return;
        }

        const admin_data = {
            mail: adminEmail,
            password: adminPassword,
        };

        try {

            let dupRes;

            if(inputType === "correo electrónico")
            {   
            dupRes = await fetch("/checkDuplicates", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input : user })
            });
            } 
            else if (inputType === "servicio")
            {   
            dupRes = await fetch("/checkDuplicatedService", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input : user })
            });
            }

            const dupData = await dupRes.json();

            if (dupData === 1) {  // Duplicado encontrado
                errorMsgBlock.textContent = `El ${inputType} ingresado ya está en uso, elija otro por favor.`;
                errorMsgBlock.style.display = "block";
                return;
            }
        } catch (err) {
            errorMsgBlock.textContent = "Error de conexión al validar correo electrónico.";
            errorMsgBlock.style.display = "block";
            return;
        }

        try {
            const adminRes = await fetch("/login_admin_validation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(admin_data)
            });

            const adminData = await adminRes.json();

            if (adminData !== 0) {
                errorMsgBlock.textContent = "Credenciales de administrador incorrectas.";
                errorMsgBlock.style.display = "block";
                return;
            }
        } catch (err) {
            errorMsgBlock.textContent = "Error de conexión al validar credenciales de administrador.";
            errorMsgBlock.style.display = "block";
            return;
        }

        // allokay
        errorMsgBlock.style.display = "none";
        HTMLFormElement.prototype.submit.call(form);
    });
}


export function checkFormAdmin(formId, emailInput, passwordInput, errorMsgId) {
    document.getElementById(formId).addEventListener("submit", async function (e) {
        e.preventDefault(); // Bloquea el envío inicial

        const mail = document.getElementById(emailInput).value.trim();
        const password = document.getElementById(passwordInput).value.trim();
        const mensajeError = document.getElementById(errorMsgId);

        
        if (!mail || !password ) {
            mensajeError.textContent = "Debe llenar ambos campos de credenciales de administrador.";
            mensajeError.style.display = "block";
            return;
        }

        const payload = {
            mail: mail,
            password: password,
        };

        try {
            const respuesta = await fetch("/login_admin_validation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await respuesta.json();

            if (data === 0) {
                mensajeError.style.display = "none";
                this.submit();
            } else {
                mensajeError.textContent = "Credenciales de administrador incorrectas.";
                mensajeError.style.display = "block";
            }
        } catch (err) {
            mensajeError.textContent = "Error de conexión. Intenta de nuevo.";
            mensajeError.style.display = "block";
        }
    });
}

export function checkDuplicatedUser(formId,inputData,errorMsgId,inputType,adminEmailInput,adminPasswordInput, passwordId) {
    const form = document.getElementById(formId);
    const errorMsgBlock = document.getElementById(errorMsgId);

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); 

        const user = document.getElementById(inputData).value.trim();
        const adminEmail = document.getElementById(adminEmailInput).value.trim();
        const adminPassword = document.getElementById(adminPasswordInput).value.trim();
        const password = document.getElementById(passwordId).value.trim();

        if (!user || !adminEmail || !adminPassword || !password) {
            errorMsgBlock.textContent = "Debe llenar todos los campos con datos válidos.";
            errorMsgBlock.style.display = "block";
            return;
        }

        const admin_data = {
            mail: adminEmail,
            password: adminPassword,
        };

        try {

            let dupRes;

            if(inputType === "correo electrónico")
            {   
            dupRes = await fetch("/checkDuplicates", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input : user })
            });
            } 
            else if (inputType === "servicio")
            {   
            dupRes = await fetch("/checkDuplicatedService", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ input : user })
            });
            }

            const dupData = await dupRes.json();

            if (dupData === 1) {  // Duplicado encontrado
                errorMsgBlock.textContent = `El ${inputType} ingresado ya está en uso, elija otro por favor.`;
                errorMsgBlock.style.display = "block";
                return;
            }
        } catch (err) {
            errorMsgBlock.textContent = "Error de conexión al validar correo electrónico.";
            errorMsgBlock.style.display = "block";
            return;
        }

        try {
            const respuesta = await fetch("/passwordStrength", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({value: password})
            });

            const strongPassword = await respuesta.json();

            if (strongPassword === 0) {
                errorMsgBlock.textContent = "Su contraseña es débil, debe ser de al menos 10 carácteres, incluir al menos una mayúscula, una minúscula, un número y un carácter especial.";
                errorMsgBlock.style.display = "block";
                return;
            }
        } catch (err) {
            errorMsgBlock.textContent = "Error de conexión en la comprobación de contraseña. Intenta de nuevo.";
            errorMsgBlock.style.display = "block";
            return;
        }

        try {
            const adminRes = await fetch("/login_admin_validation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(admin_data)
            });

            const adminData = await adminRes.json();

            if (adminData !== 0) {
                errorMsgBlock.textContent = "Credenciales de administrador incorrectas.";
                errorMsgBlock.style.display = "block";
                return;
            }
        } catch (err) {
            errorMsgBlock.textContent = "Error de conexión al validar credenciales de administrador.";
            errorMsgBlock.style.display = "block";
            return;
        }

        // allokay
        errorMsgBlock.style.display = "none";
        HTMLFormElement.prototype.submit.call(form);
    });
}