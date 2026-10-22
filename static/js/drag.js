function updateFileName(input, filenameId) {
  const filenameDiv = document.getElementById(filenameId);
  const uploadBox = input.closest(".custom-file-upload");

  if (input.files.length > 0) {
    const fileName = input.files[0].name;
    filenameDiv.textContent = `📄 ${fileName}`;
    filenameDiv.style.display = "block";
    uploadBox.classList.add("file-selected");

    // Cambiar el texto principal
    const textDiv = uploadBox.querySelector(".file-upload-text");
    textDiv.textContent = "Archivo seleccionado";
  } else {
    filenameDiv.style.display = "none";
    uploadBox.classList.remove("file-selected");
  }
}

document.querySelectorAll(".custom-file-upload").forEach((uploadBox) => {
  const input = uploadBox.querySelector('input[type="file"]');

  uploadBox.addEventListener("dragover", function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add("dragover");
  });

  uploadBox.addEventListener("dragleave", function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove("dragover");
  });

  uploadBox.addEventListener("drop", function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove("dragover");

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      input.files = files;
      const event = new Event("change", { bubbles: true });
      input.dispatchEvent(event);
    }
  });
});
