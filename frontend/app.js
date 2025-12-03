// frontend/app.js
// Handles the UI for CreativeForge: file uploads, POST /generate, progress, and ZIP download.

(() => {
  const generateBtn = document.getElementById("generateBtn");
  const statusEl = document.getElementById("status");
  const previewEl = document.getElementById("preview");
  const progressWrap = document.getElementById("progressWrap");
  const bar = document.getElementById("bar");
  const downloadArea = document.getElementById("downloadArea");
  const downloadLink = document.getElementById("downloadLink");

  function setStatus(text, muted = false) {
    statusEl.textContent = text;
    if (muted) {
      statusEl.style.opacity = "0.8";
    } else {
      statusEl.style.opacity = "1";
    }
  }

  async function streamDownloadBlob(response, filename) {
    // Convert response to blob and create URL for download
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadArea.style.display = "block";
    // Trigger automatic download
    downloadLink.click();
    // Keep URL alive for a short time; user can still click link again
    setTimeout(() => URL.revokeObjectURL(url), 1000 * 60); // revoke after 60s
  }

  generateBtn.addEventListener("click", async () => {
    // Reset UI
    previewEl.innerHTML = "";
    downloadArea.style.display = "none";
    bar.style.width = "0%";
    setStatus("Ready");

    const logoInput = document.getElementById("logo");
    const productInput = document.getElementById("product");
    const brand = document.getElementById("brand").value || "";
    const tone = document.getElementById("tone").value || "premium";
    const preset = document.getElementById("preset").value || "B3";

    if (!logoInput.files.length || !productInput.files.length) {
      alert("Please upload both logo and product images.");
      return;
    }

    // Build form data
    const form = new FormData();
    form.append("logo", logoInput.files[0]);
    form.append("product", productInput.files[0]);
    form.append("brand_name", brand);
    form.append("tone", tone);
    form.append("preset", preset);
    // enforce exactly 10 creatives on server side; still send count for clarity
    form.append("count", "10");

    setStatus("Uploading files…");
    generateBtn.disabled = true;
    progressWrap.style.display = "block";
    bar.style.width = "10%";

    try {
      const resp = await fetch("http://localhost:8000/generate", {
        method: "POST",
        body: form,
      });

      if (!resp.ok) {
        const text = await resp.text();
        setStatus("Server error", true);
        alert("Server error: " + resp.status + " — " + text);
        return;
      }

      setStatus("Generating images & captions…");
      bar.style.width = "40%";

      // Stream the zip blob and trigger download
      await streamDownloadBlob(resp, "creative_pack.zip");

      setStatus("Complete — ZIP downloaded");
      bar.style.width = "100%";

    } catch (err) {
      console.error("Request failed:", err);
      setStatus("Failed", true);
      alert("Request failed: " + (err && err.message ? err.message : err));
    } finally {
      generateBtn.disabled = false;
      progressWrap.style.display = "none";
    }
  });

  // Optional: preview thumbnails for local files before upload
  const logoInputEl = document.getElementById("logo");
  const productInputEl = document.getElementById("product");

  function previewLocalFiles() {
    previewEl.innerHTML = "";
    const files = [];
    if (logoInputEl.files.length) files.push(logoInputEl.files[0]);
    if (productInputEl.files.length) files.push(productInputEl.files[0]);

    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.style.width = "120px";
        img.style.height = "auto";
        img.style.objectFit = "contain";
        img.style.borderRadius = "6px";
        previewEl.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  }

  logoInputEl.addEventListener("change", previewLocalFiles);
  productInputEl.addEventListener("change", previewLocalFiles);

})();
