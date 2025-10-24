// ---------------- Ambil CSRF Token ----------------
function getCSRFToken() {
  const name = "csrftoken=";
  const decoded = decodeURIComponent(document.cookie);
  const cookies = decoded.split(";");
  for (let c of cookies) {
    c = c.trim();
    if (c.indexOf(name) === 0) return c.substring(name.length, c.length);
  }
  return "";
}

// ---------------- Lihat Detail ----------------
function lihatDetail(eventId) {
  console.log("🔵 Lihat detail diklik, id =", eventId);

  const container = document.getElementById("event-detail");
  if (!container) {
    console.error("❌ Elemen #event-detail tidak ditemukan!");
    return;
  }

  container.innerHTML = `
    <div class="p-4 border rounded-lg bg-gray-50 relative">
      <button onclick="document.getElementById('event-detail').innerHTML=''" 
              class="absolute top-2 right-2 bg-red-600 text-white rounded px-2 py-1 cursor-pointer">
        ✕ Close
      </button>
      <div id="event-detail-content" class="text-gray-800 font-medium">Memuat...</div>
    </div>
  `;

  fetch(`/upcoming-event/get-event-json/${eventId}/`)
    .then(res => res.json())
    .then(data => {
      console.log("✅ Detailed data received:", data);

      const contentDiv = document.getElementById("event-detail-content");
      if (!contentDiv) {
        console.error("❌ Tidak ketemu #event-detail-content");
        return;
      }

      let html = `
        <h3 class="text-xl font-bold mb-2">${data.name}</h3>
        <p><strong>Organizer:</strong> ${data.organizer}</p>
        <p>📍Location: ${data.location}</p>
        <p>🗓️ Date: ${data.date}</p>
        <p><strong>Sports:</strong> ${data.sport_branch}</p>
        ${data.description ? `<p class="mt-2">${data.description}</p>` : "<p class='mt-2 text-gray-500 italic'>(Belum ada deskripsi)</p>"}
      `;

      if (data.image_url) {
        html = `<img src="${data.image_url}" alt="${data.name}" class="w-full max-h-56 object-cover rounded mb-4">` + html;
      }

      contentDiv.innerHTML = html;
      console.log("🟢 Detail event sudah diisi ke DOM");
    })
    .catch(err => {
      console.error("❌ Error ambil detail:", err);
    });
}

// ---------------- Hapus Event ----------------
function hapusEvent(eventId) {
  console.log("🔴 Klik hapus event id =", eventId);
  showConfirmToast("Are you sure you want to delete this event?", () => {
    fetch(`/upcoming-event/${eventId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCSRFToken() },
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("🗑️ Respons hapus:", data);
        if (data.success) {
          document.querySelector(`.event-card[data-id="${eventId}"]`)?.remove();
          if (document.querySelectorAll(".event-card").length === 0) {
            document.getElementById("event-list").innerHTML =
              '<p class="text-center text-gray-500 col-span-full">Belum ada event yang akan datang.</p>';
          }
          showToast("Event successfully deleted!");
        } else {
          showToast(data.message || "Gagal menghapus event.", "error");
        }
      })
      .catch((err) => {
        console.error("🔥 Error hapus:", err);
        showToast("Terjadi kesalahan server.", "error");
      });
  });
}

// ---------------- Listener ----------------
function attachEventListeners() {
  const detailBtns = document.querySelectorAll(".lihat-detail-btn");
  const hapusBtns = document.querySelectorAll(".hapus-event-btn");

  console.log(`🎯 Ketemu ${detailBtns.length} tombol detail dan ${hapusBtns.length} tombol hapus`);

  detailBtns.forEach((btn) => (btn.onclick = () => lihatDetail(btn.dataset.id)));
  hapusBtns.forEach((btn) => (btn.onclick = () => hapusEvent(btn.dataset.id)));
}

// ---------------- addEventListener ----------------
document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM Loaded, pasang listener tombol...");
  attachEventListeners();
});

// ---------------- Tambah Event ----------------
window.addEventListener("message", (event) => {
  if (event.data.type === "NEW_EVENT") {
    const e = event.data.event;
    const eventList = document.getElementById("event-list");
    const newCard = document.createElement("div");
    newCard.className = "event-card border-2 border-gray-400 rounded-lg p-4 bg-gray-50";
    newCard.dataset.id = e.id;
    newCard.innerHTML = `
      ${e.image_url ? `<img src="${e.image_url}" class="w-full h-36 object-cover rounded mb-2">` : ""}
      <h3 class="text-lg font-semibold text-[#0A1A3C]">${e.name}</h3>
      <p class="text-gray-600">📅 ${e.date}</p>
      <p class="text-gray-600">📍 ${e.location}</p>
      <div class="mt-2 flex items-center gap-2">
        <button class="lihat-detail-btn text-[#0A1A3C] font-medium underline cursor-pointer"
                data-id="${e.id}">Lihat Detail</button>
        <a href="/upcoming-event/${e.id}/edit/" class="text-blue-600 font-medium">Edit</a>
        <button class="hapus-event-btn text-red-600 font-medium cursor-pointer"
                data-id="${e.id}">Hapus</button>
      </div>
    `;
    eventList.prepend(newCard);
    attachEventListeners();
    showToast("New event succesfully added!");
  }
});

window.lihatDetail = lihatDetail;
window.hapusEvent = hapusEvent;
