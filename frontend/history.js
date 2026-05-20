// Protect history page
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

// Fetch prediction history
fetch("http://localhost:8000/predictions", {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
        "token": token,
        "api-key": "demo-key"
    }
})
.then(res => {
    if (!res.ok) {
        throw new Error("Failed to fetch history");
    }
    return res.json();
})
.then(data => {
    const list = document.getElementById("history-list");

    if (data.length === 0) {
        list.innerHTML = "<li>No predictions found</li>";
        return;
    }

    data.forEach(item => {
        const li = document.createElement("li");
        li.innerText = `Prediction ID: ${item.id} | Price: ${item.predicted_price}`;
        list.appendChild(li);
    });
})
.catch(err => {
    console.error(err);
    alert("Please login again");
    localStorage.removeItem("token");
    window.location.href = "login.html";
});

// Back button handler
function goBack() {
    window.location.href = "predict.html";
}
