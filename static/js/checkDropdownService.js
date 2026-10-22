export function addDropdownValidationPassword(selectId, errorMsgId, dropdownType, formId, emailId, passwordId) {
    document.addEventListener("DOMContentLoaded", function () {
        const select = document.getElementById(selectId);
        const errorMsgBlock = document.getElementById(errorMsgId);

        if (!select) {
            console.error(`No se encontró el elemento con id "${selectId}"`);
            return;
        }

        errorMsgBlock.textContent = "";
        errorMsgBlock.style.display = "none";
        
        select.addEventListener('change', function () {
            if (select.selectedIndex === 0) {
                select.setCustomValidity(`Por favor, selecciona un ${dropdownType} válido.`);
                errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
                errorMsgBlock.style.display = "block";
            } else {
                select.setCustomValidity("");
                errorMsgBlock.textContent = "";
                errorMsgBlock.style.display = "none";
            }
        });

        // Sending form
        if (select.form) {
            select.form.addEventListener('submit', async function (event) {
                event.preventDefault();

                // Dropdown option
                if (select.selectedIndex === 0) {
                    event.preventDefault();
                    errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
                    errorMsgBlock.style.display = "block";
                    return;
                }

                // Admin Validation
                const mail = document.getElementById(emailId).value.trim();
                const password = document.getElementById(passwordId).value.trim();

                if(!mail || !password) {
                    errorMsgBlock.textContent = "Debe llenar todos los campos con datos válidos.";
                    errorMsgBlock.style.display = "block";
                    return;
                }

                const admin_data = {
                    mail: mail,
                    password: password,
                };

                // Admin credentials check
                try {
                    const adminRes = await fetch("/login_admin_validation", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(admin_data)
                    } );

                    const adminValidation = await adminRes.json();

                    if (adminValidation !== 0) {
                        errorMsgBlock.textContent = "Credenciales de administrador incorrectas.";
                        errorMsgBlock.style.display = "block";
                        return;
                    }
                } catch (err) {
                    errorMsgBlock.textContent = "Error al validar credenciales de administrador.";
                    errorMsgBlock.style.display = "block";
                    return;
                }

                // All OK
                errorMsgBlock.style.display = "none";
                HTMLFormElement.prototype.submit.call(select.form);

            });
        }
    });
}

// Dropdown option validation
export function addDropdownValidation(selectId, errorMsgId, dropdownType, onValid) {
    document.addEventListener("DOMContentLoaded", function () {
        const select = document.getElementById(selectId);
        const errorMsgBlock = document.getElementById(errorMsgId);

        if (!select || !errorMsgBlock) {
            console.error("Error: elemento no encontrado en dropdownValidation");
            return;
        }

        errorMsgBlock.style.display = "none";

        select.addEventListener("change", function () {
            if (select.selectedIndex === 0) {
                errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
                errorMsgBlock.style.display = "block";
            } else {
                errorMsgBlock.textContent = "";
                errorMsgBlock.style.display = "none";
            }
        });

        if (select.form) {
            select.form.addEventListener("submit", function (event) {
                event.preventDefault();

                if (select.selectedIndex === 0) {
                    errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
                    errorMsgBlock.style.display = "block";
                    return;
                }

                // Valid dropdown option
                onValid(select.form, errorMsgBlock);
            });
        }
    });
}

// Consecutive dropdown Validation
export function addDropdownValidationConsecutive(form,errorMsgBlock,selectId,dropdownType,onValid) {
    const select = document.getElementById(selectId);

    if (!select || !errorMsgBlock) {
        console.error("Error: elemento no encontrado en consecutiveDropdownValidation");
        return;
    }

    
    select.addEventListener("change", function () {
        if (select.selectedIndex === 0) {
            errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
            errorMsgBlock.style.display = "block";
        } else {
            errorMsgBlock.textContent = "";
            errorMsgBlock.style.display = "none";
        }
    });

    
    if (select.selectedIndex === 0) {
        errorMsgBlock.textContent = `Por favor, selecciona un ${dropdownType} válido.`;
        errorMsgBlock.style.display = "block";
        return;
    }

    onValid(form, errorMsgBlock);
}


// Admin Validation
export async function adminValidation(form,errorMsgBlock,emailId,passwordId) {
    const mail = document.getElementById(emailId).value.trim();
    const password = document.getElementById(passwordId).value.trim();


    if (!mail || !password) {
        errorMsgBlock.textContent = "Debe llenar todos los campos con datos válidos.";
        errorMsgBlock.style.display = "block";
        return;
    }

    const adminData = {
        mail: mail,
        password: password,
    };

    try {
        const adminRes = await fetch("/login_admin_validation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(adminData)
        });

        const adminValidation = await adminRes.json();

        if (adminValidation !== 0) {
            errorMsgBlock.textContent = "Credenciales de administrador incorrectas.";
            errorMsgBlock.style.display = "block";
            return;
        }

    } catch (err) {
        errorMsgBlock.textContent =
            "Error de conexión al validar credenciales de administrador.";
        errorMsgBlock.style.display = "block";
        return;
    }

    // All OK, submit
    errorMsgBlock.style.display = "none";
    HTMLFormElement.prototype.submit.call(form);
}


// Duplicated field or quarter validation
export async function checkDuplicatedFieldDropdown(form, errorMsgBlock, selectedService, fieldInput, onValid) {
    const service = document.getElementById(selectedService);
    const field = document.getElementById(fieldInput);

    if (!service || !field || !errorMsgBlock) {
        console.error("Error: elemento no encontrado en checkDuplicatedFieldDropdown");
        return;
    }

    const userRequest = {
        service: service.value,
        field: field.value,
    };

    try {
        const respuesta = await fetch("/checkDuplicatedField", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userRequest)
        });

        const duplicatedField = await respuesta.json();

        if (duplicatedField === 1) {  
            // Campo duplicado
            errorMsgBlock.textContent = "El campo ingresado ya está en uso, elija otro por favor.";
            errorMsgBlock.style.display = "block";
            return;
        }

        if (duplicatedField === 0) {  
            // Disponible
            errorMsgBlock.style.display = "none";

            // Continuar con la siguiente validación
            await onValid(form, errorMsgBlock);
        }

    } catch (err) {
        errorMsgBlock.textContent = "Error de conexión en la consulta de campos. Intenta de nuevo.";
        errorMsgBlock.style.display = "block";
        return;
    }
}

export async function checkDuplicatedQuarterDropdown(form, errorMsgBlock, selectedUser, selectedService, selectedField, quarter_input, onValid) {
    const mail = document.getElementById(selectedUser);
    const service = document.getElementById(selectedService);
    const field = document.getElementById(selectedField);
    const quarter = document.getElementById(quarter_input);

    if (!service || !field || !mail || !quarter || !errorMsgBlock) {
        console.error("Error: elemento no encontrado en checkDuplicatedFieldDropdown");
        return;
    }

    const userRequest = {
        mail: mail.value,
        service: service.value,
        field: field.value,
        quarter: quarter.value,
    };

    try {
        const respuesta = await fetch("/checkDuplicatedQuarter", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userRequest)
        });

        const duplicatedQuarter = await respuesta.json();

        if (duplicatedQuarter === 1) {  
            // Campo duplicado
            errorMsgBlock.textContent = "El cuartel ingresado ya está en uso, elija otro por favor.";
            errorMsgBlock.style.display = "block";
            return;
        }

        if (duplicatedQuarter === 0) {  
            // Disponible
            errorMsgBlock.style.display = "none";

            // Continuar con la siguiente validación
            await onValid(form, errorMsgBlock);
        }

    } catch (err) {
        errorMsgBlock.textContent = "Error de conexión en la consulta de cuarteles. Intenta de nuevo.";
        errorMsgBlock.style.display = "block";
        return;
    }
}

export async function checkPasswordStrength(form, errorMsgBlock, passwordInput, onValid) {
    const password = document.getElementById(passwordInput);

    if (!password) {
        console.error("Error: elemento no encontrado en checkPasswordStrength");
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
            // Campo duplicado
            errorMsgBlock.textContent = "Su contrasena es debil, debe incluir al menos una mayúscula, una minúscula, un número y un carácter especial.";
            errorMsgBlock.style.display = "block";
            return;
        }

        if (strongPassword === 1) {  
            // Disponible
            errorMsgBlock.style.display = "none";

            // Continuar con la siguiente validación
            await onValid(form, errorMsgBlock);
        }

    } catch (err) {
        errorMsgBlock.textContent = "Error de conexión en la comprobación de contraseña. Intenta de nuevo.";
        errorMsgBlock.style.display = "block";
        return;
    }
}