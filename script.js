document
    .getElementById("alertForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const symbol =
            document.getElementById("symbol").value;

        const targetPrice =
            document.getElementById("target_price").value;

        const condition =
            document.getElementById("condition_type").value;

        const response = await fetch("/api/alerts", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                symbol: symbol,
                target_price: targetPrice,
                condition_type: condition

            })

        });

        const data = await response.json();

        document.getElementById("message").textContent =
            data.message || data.error;

        if (response.ok) {

            document
                .getElementById("alertForm")
                .reset();

            loadAlerts();
        }

    });


async function loadAlerts() {

    const response =
        await fetch("/api/alerts");

    const alerts =
        await response.json();

    const table =
        document.getElementById("alertsTable");

    table.innerHTML = "";

    alerts.forEach(alert => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${alert.symbol}</td>
            <td>${alert.target_price}</td>
            <td>${alert.condition_type}</td>
            <td>${alert.status}</td>
        `;

        table.appendChild(row);

    });
}


loadAlerts();