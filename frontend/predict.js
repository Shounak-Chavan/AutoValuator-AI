// Protect page
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}
function goToHistory() {
    window.location.href = "history.html";
}

// Call predict API
function predict() {
    fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "api-key": "demo-key",
            "token": localStorage.getItem("token")
            },
        body: JSON.stringify({
            company: document.getElementById("company").value,
            year: Number(document.getElementById("year").value),
            owner: document.getElementById("owner").value,
            fuel: document.getElementById("fuel").value,
            seller_type: document.getElementById("seller_type").value,
            transmission: document.getElementById("transmission").value,
            km_driven: Number(document.getElementById("km_driven").value),
            mileage_mpg: Number(document.getElementById("mileage_mpg").value),
            engine_cc: Number(document.getElementById("engine_cc").value),
            max_power_bhp: Number(document.getElementById("max_power_bhp").value),
            torque_nm: Number(document.getElementById("torque_nm").value),
            seats: Number(document.getElementById("seats").value)
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized or error");
        return res.json();
    })
    .then(data => {
        document.getElementById("result").innerText =
            "Predicted Price: " + data.predicted_price;
    })
    .catch(err => {
        console.error(err);
        document.getElementById("result").innerText =
            "Error: Please login again";
    });
}
