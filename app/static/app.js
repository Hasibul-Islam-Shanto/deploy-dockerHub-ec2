function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }
    return data;
}

function confirmAction(message) {
    return window.confirm(message);
}

function refreshStudents() {
    const search = document.getElementById("studentSearch")?.value || "";
    const url = search ? `/students?search=${encodeURIComponent(search)}` : "/students";
    return fetch(url)
        .then(r => r.text())
        .then(html => {
            document.getElementById("studentsTable").innerHTML = html;
        });
}

function refreshAttendance() {
    const search = document.getElementById("attendanceSearch")?.value || "";
    const date = document.getElementById("attendanceDate")?.value || "";
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (date) params.set("date", date);
    const query = params.toString();
    const url = query ? `/get_attendance?${query}` : "/get_attendance";
    return fetch(url)
        .then(r => r.text())
        .then(html => {
            document.getElementById("attendanceTable").innerHTML = html;
        });
}

function refreshDashboard() {
    return Promise.all([refreshStudents(), refreshAttendance()]);
}

function registerStudent() {
    const input = document.getElementById("studentName");
    const name = input.value.trim();
    if (!name) {
        showToast("Please enter a student name", "error");
        return;
    }

    apiRequest("/register_student", {
        method: "POST",
        body: JSON.stringify({ name }),
    })
        .then(data => {
            showToast(data.message);
            input.value = "";
            refreshDashboard();
            updateStats();
        })
        .catch(err => showToast(err.message, "error"));
}

function markAttendance(studentId, status) {
    apiRequest("/mark_attendance", {
        method: "POST",
        body: JSON.stringify({ student_id: studentId, status }),
    })
        .then(data => {
            showToast(data.message);
            refreshDashboard();
            updateStats();
        })
        .catch(err => showToast(err.message, "error"));
}

function deleteStudent(studentId, name) {
    if (!confirmAction(`Delete ${name}? This removes all their attendance records.`)) return;

    apiRequest(`/students/${studentId}`, { method: "DELETE" })
        .then(data => {
            showToast(data.message);
            refreshDashboard();
            updateStats();
        })
        .catch(err => showToast(err.message, "error"));
}

function deleteAttendanceRecord(attendanceId) {
    if (!confirmAction("Delete this attendance record?")) return;

    apiRequest(`/attendance/${attendanceId}`, { method: "DELETE" })
        .then(data => {
            showToast(data.message);
            refreshDashboard();
            updateStats();
        })
        .catch(err => showToast(err.message, "error"));
}

function openEditModal(studentId, currentName) {
    document.getElementById("editStudentId").value = studentId;
    document.getElementById("editStudentName").value = currentName;
    document.getElementById("editModal").classList.add("open");
}

function closeEditModal() {
    document.getElementById("editModal").classList.remove("open");
}

function saveStudentEdit() {
    const studentId = document.getElementById("editStudentId").value;
    const name = document.getElementById("editStudentName").value.trim();
    if (!name) {
        showToast("Name cannot be empty", "error");
        return;
    }

    apiRequest(`/students/${studentId}`, {
        method: "PUT",
        body: JSON.stringify({ name }),
    })
        .then(data => {
            showToast(data.message);
            closeEditModal();
            refreshDashboard();
        })
        .catch(err => showToast(err.message, "error"));
}

function updateStats() {
    fetch("/")
        .then(r => r.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const stats = doc.querySelector(".stats-grid");
            if (stats) {
                document.querySelector(".stats-grid").innerHTML = stats.innerHTML;
            }
        });
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("studentsTable")) {
        refreshDashboard();
    }

    document.getElementById("editModal")?.addEventListener("click", (e) => {
        if (e.target.id === "editModal") closeEditModal();
    });

    document.addEventListener("click", (e) => {
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
            openEditModal(editBtn.dataset.id, editBtn.dataset.name);
            return;
        }
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            deleteStudent(deleteBtn.dataset.id, deleteBtn.dataset.name);
        }
    });
});
