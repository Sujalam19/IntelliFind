const API = "http://127.0.0.1:5000";

/* ================= LOGIN OTP ================= */

function sendOTP() {
  const email = document.getElementById("email").value;

  if (!email) {
    alert("Enter email");
    return;
  }

  localStorage.setItem("email", email);

  fetch(API + "/send-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  })
  .then(() => {
    window.location.href = "otp.html";
  });
}

function verifyOTP() {
  const otp = document.getElementById("otp").value;
  const email = localStorage.getItem("email");

  fetch(API + "/verify-otp", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp })
  })
  .then(res => {
    if (!res.ok) throw new Error();
    window.location.href = "dashboard.html";
  })
  .catch(() => alert("Invalid OTP"));
}

/* ================= SUBMIT LOST / FOUND ================= */

function submitItem() {
  const type = document.getElementById("type").value;
  const description = document.getElementById("description").value;
  const email = localStorage.getItem("email");

  if (!description) {
    alert("Enter description");
    return;
  }

  fetch(API + "/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type,
      description,
      email,
      college_id: email.split("@")[1]
    })
  })
  .then(res => res.json())
  .then(data => {
    localStorage.setItem("collection_point", data.collection_point);
    localStorage.setItem("claim_code", data.claim_code);
    window.location.href = "success.html";
  })
  .catch(() => alert("Submit failed"));
}