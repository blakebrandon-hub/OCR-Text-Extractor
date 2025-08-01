function uploadImage() {
  const input = document.getElementById('imageInput');
  const file = input.files[0];
  if (!file) return alert("Please select an image");

  const formData = new FormData();
  formData.append('image', file);

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) throw new Error("Server returned an error");
    return response.json();
  })
  .then(data => {
    const output = document.getElementById('output');
    if (data.success) {
      output.textContent = JSON.stringify(data, null, 2);
    } else {
      output.textContent = `Error: ${data.error}`;
    }
  })
  .catch(err => {
    document.getElementById('output').textContent = `Fetch error: ${err}`;
    console.error("❌ Fetch failed:", err);
  });
}
