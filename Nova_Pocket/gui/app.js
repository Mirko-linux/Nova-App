document.getElementById('upload-btn').addEventListener('click', () => {
  document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // Esempio: chiamata API al backend Rust
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8080/upload', {
      method: 'POST',
      body: formData
    });
    console.log(await response.json());
  } catch (error) {
    console.error("Upload failed:", error);
  }
});
