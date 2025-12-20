// Ambil CSRF Token dari Cookie (untuk AJAX)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");


// Tambah / Edit Polling
document.addEventListener("submit", function (e) {
  if (e.target.matches("#poll-form-container form")) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    
    const isEdit = form.querySelector("input[name=poll_id]") !== null;
    formData.append(isEdit ? "save_edit" : "add_poll", "1");

    fetch("", {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          showNotification(data.message);

          if (data.poll_id) {
            
            const pollCard = document.querySelector(
              `.poll-card input[value='${data.poll_id}']`
            )?.closest(".poll-card");

            if (pollCard) {
              pollCard.querySelector("h3").textContent = data.question;

              const ul = pollCard.querySelector("ul");
              ul.innerHTML = data.options
                .map(
                  (opt) =>
                    `<li>
                      <span>${opt.option_text}</span>
                      <span class="text-sm text-gray-600">${opt.votes} votes</span>
                    </li>`
                )
                .join("");
            }
          } else if (data.html) {
            
            const container = document.querySelector(".admin-poll-section .flex-col");
            if (container) container.insertAdjacentHTML("afterbegin", data.html);
          }

          
          const formContainer = document.getElementById("poll-form-container");
          const form = formContainer.querySelector("form");

          form.reset();

         
          const optionsContainer = form.querySelector("#options-container");
          if (optionsContainer) {
            optionsContainer.innerHTML = `
              <label class="block font-medium text-gray-700">Opsi Jawaban</label>
              <input type="text" name="options[]" class="option-input border rounded-lg w-full p-2 mt-2" placeholder="Masukkan opsi jawaban" required>
            `;
          }

        
          const hiddenPollId = form.querySelector("input[name='poll_id']");
          if (hiddenPollId) hiddenPollId.remove();

          document.getElementById("poll-form-title").textContent = "Tambah Polling Baru";
          const submitBtn = form.querySelector("button[type='submit']");
          submitBtn.textContent = "Simpan Polling";

          const cancelBtn = document.getElementById("cancel-form-btn");
          if (cancelBtn) cancelBtn.classList.add("hidden");

        
          formContainer.classList.add("hidden");
         
        } else {
          showNotification("⚠️ Gagal menyimpan polling.");
        }
      })

      .catch((err) => {
        console.error("Terjadi kesalahan server:", err);
        showNotification("🚨 Terjadi kesalahan server.");
      });
  }
});

// Hapus Polling
document.addEventListener("click", function (e) {
  if (e.target.matches(".btn-delete")) {
    e.preventDefault();
    const form = e.target.closest("form");

    fetch(form.action, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          showNotification(data.message);
          form.closest(".poll-card").remove();
        }
      })
      .catch((err) => console.error(err));
  }
});

// Edit Polling (tampilkan form edit AJAX)
document.addEventListener("submit", function (e) {
  if (e.target.matches("form[action='']") && e.submitter?.name === "edit_poll") {
    e.preventDefault();
    const form = e.target;
    const pollId = form.querySelector("input[name='poll_id']").value;


    const pollCard = form.closest(".poll-card");
    const question = pollCard.querySelector("h3").textContent.trim();
    const options = Array.from(pollCard.querySelectorAll("ul li"))
      .map((li) => li.querySelector("span:first-child").textContent.trim());


    const formContainer = document.getElementById("poll-form-container");
    const questionInput = formContainer.querySelector("input[name='question']");
    const optionsContainer = formContainer.querySelector("#options-container");

    formContainer.classList.remove("hidden");
    formContainer.scrollIntoView({ behavior: "smooth" });

    // isi data
    questionInput.value = question;

    optionsContainer.innerHTML = `
      <label class="block font-medium text-gray-700">Opsi Jawaban</label>
      ${options
        .map(
          (opt) =>
            `<input type="text" name="options[]" value="${opt}" class="option-input border rounded-lg w-full p-2 mt-2" required>`
        )
        .join("")}
    `;

    if (!formContainer.querySelector("input[name='poll_id']")) {
      const hiddenId = document.createElement("input");
      hiddenId.type = "hidden";
      hiddenId.name = "poll_id";
      hiddenId.value = pollId;
      formContainer.querySelector("form").appendChild(hiddenId);
    } else {
      formContainer.querySelector("input[name='poll_id']").value = pollId;
    }

    const submitBtn = formContainer.querySelector("button[type='submit']");
    submitBtn.textContent = "Simpan Perubahan";

    document.getElementById("poll-form-title").textContent = "Edit Polling";
    document.getElementById("cancel-form-btn")?.classList.remove("hidden");
  }
});

// Notifikasi 
function showNotification(message, type = "success") {
  const notif = document.createElement("div");

  // Warna tema berdasarkan tipe 
  const colors = {
    success: "bg-white/60 border-green-400 text-green-800",
    error: "bg-white/60 border-red-400 text-red-800",
    warning: "bg-white/60 border-yellow-400 text-yellow-800",
    info: "bg-white/60 border-blue-400 text-blue-800",
  };

  notif.className = `
    fixed bottom-6 right-6 
    px-5 py-3 rounded-2xl shadow-xl border 
    backdrop-blur-lg
    transition-all duration-500 ease-out 
    animate-fade z-50 
    font-medium text-sm md:text-base
    ${colors[type] || colors.success}
  `;
  notif.innerHTML = `
    <div class="flex items-center space-x-3">
      <span>${
        type === "success"
          ? "✅"
          : type === "error"
          ? "❌"
          : type === "warning"
          ? "⚠️"
          : "ℹ️"
      }</span>
      <span>${message}</span>
    </div>
  `;

  document.body.appendChild(notif);

  
  setTimeout(() => {
    notif.style.opacity = "0";
    notif.style.transform = "translateY(10px)";
    setTimeout(() => notif.remove(), 500);
  }, 3000);
}

//  Voting AJAX (User)
document.addEventListener("click", function (e) {
  if (e.target.matches(".vote-btn")) {
    const btn = e.target;
    const optionId = btn.dataset.optionId;

    fetch(`/vote/${optionId}/`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          const voteResult = document.getElementById("vote-result");
          if (voteResult) {
            voteResult.textContent = `Terima kasih sudah memilih! Total votes: ${data.total_votes}`;
            voteResult.classList.remove("hidden");
          }

          document.querySelectorAll(".vote-btn").forEach((b) => {
            b.disabled = true;
            b.classList.add("opacity-50", "cursor-not-allowed");
          });

          showNotification("🏅 Vote kamu sudah terekam!");

          setTimeout(() => hideModal(), 1500);
        }
      })
      .catch((err) => {
        console.error("Error voting:", err);
        showNotification("🚨 Gagal mengirim vote.");
      });
  }

  
  if (e.target.matches("#close-poll")) {
    hideModal();
  }
});


function showModal() {
  const modal = document.getElementById("poll-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  setTimeout(() => {
    modal.classList.remove("opacity-0");
    modal.querySelector("div").classList.remove("scale-95");
  }, 10);
}

function hideModal() {
  const modal = document.getElementById("poll-modal");
  if (!modal) return;
  modal.classList.add("opacity-0");
  modal.querySelector("div").classList.add("scale-95");
  setTimeout(() => modal.classList.add("hidden"), 300);
}

document.addEventListener("DOMContentLoaded", showModal);

// Tombol Batal Edit
document.getElementById("cancel-edit-btn")?.addEventListener("click", function () {
  const formContainer = document.getElementById("poll-form-container");
  const form = formContainer.querySelector("form");
  const title = document.getElementById("poll-form-title");
  const cancelBtn = document.getElementById("cancel-edit-btn");
  const submitBtn = form.querySelector("button[type='submit']");

  form.reset();

  const hiddenPollId = form.querySelector("input[name='poll_id']");
  if (hiddenPollId) hiddenPollId.remove();

  title.textContent = "Tambah Polling Baru";
  submitBtn.textContent = "Simpan Polling";

  cancelBtn.classList.add("hidden");
});

document.getElementById("cancel-form-btn")?.addEventListener("click", function () {
  const formContainer = document.getElementById("poll-form-container");
  const form = formContainer.querySelector("form");
  const title = document.getElementById("poll-form-title");
  const cancelBtn = document.getElementById("cancel-form-btn");
  const submitBtn = form.querySelector("button[type='submit']");

  form.reset();

  const hiddenPollId = form.querySelector("input[name='poll_id']");
  if (hiddenPollId) hiddenPollId.remove();

  title.textContent = "Tambah Polling Baru";
  submitBtn.textContent = "Simpan Polling";

  cancelBtn.classList.add("hidden");

  formContainer.classList.add("hidden");
});
