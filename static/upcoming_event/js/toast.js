function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `fixed top-5 right-5 px-4 py-2 rounded-lg shadow-lg text-white z-50 ${
    type === "error" ? "bg-red-600" : "bg-green-600"
  }`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

function showConfirmToast(message, onConfirm) {
  const toast = document.createElement("div");
  toast.className =
    "fixed bottom-5 right-5 bg-white border shadow-lg rounded-lg p-4 z-50 flex flex-col gap-2";
  toast.innerHTML = `
    <p class="text-gray-800">${message}</p>
    <div class="flex justify-end gap-2">
    <button id="confirm-yes" class="bg-red-600 text-white px-3 py-1 rounded">Yes</button>
    <button id="confirm-no" class="bg-gray-300 text-black px-3 py-1 rounded">Cancel</button>
    </div>
  `;
  document.body.appendChild(toast);

  toast.querySelector("#confirm-yes").onclick = () => {
    onConfirm?.();
    toast.remove();
  };
  toast.querySelector("#confirm-no").onclick = () => toast.remove();
};

// biar bisa dipanggil global dari HTML & file JS lain
window.showToast = showToast;
window.showConfirmToast = showConfirmToast;
