// =====================================
// LOAD ALERTS WHEN PAGE OPENS
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadAlerts();

        loadMarketStatus();

    }
);


// =====================================
// CREATE ALERT
// =====================================

document
    .getElementById("alertForm")
    .addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const symbol =
                document
                    .getElementById("symbol")
                    .value
                    .trim()
                    .toUpperCase();


            const targetPrice =
                document
                    .getElementById("target_price")
                    .value;


            const conditionType =
                document
                    .getElementById("condition_type")
                    .value;


            const messageBox =
                document
                    .getElementById("alertMessage");


            if (!symbol || !targetPrice) {

                showMessage(
                    "Please enter all required fields.",
                    "error"
                );

                return;

            }


            try {

                const response =
                    await fetch(
                        "/api/alerts",
                        {

                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                symbol: symbol,

                                target_price:
                                    parseFloat(targetPrice),

                                condition_type:
                                    conditionType

                            })

                        }
                    );


                const data =
                    await response.json();


                if (data.success) {

                    showMessage(
                        "✅ Alert created successfully!",
                        "success"
                    );


                    document
                        .getElementById("alertForm")
                        .reset();


                    loadAlerts();

                }

                else {

                    showMessage(
                        data.message ||
                        "Could not create alert.",
                        "error"
                    );

                }


            }

            catch (error) {

                console.error(error);

                showMessage(
                    "Server error. Please try again.",
                    "error"
                );

            }

        }
    );


// =====================================
// SHOW MESSAGE
// =====================================

function showMessage(message, type) {

    const box =
        document.getElementById("alertMessage");


    box.textContent = message;

    box.className =
        "message " + type;


    setTimeout(
        function () {

            box.className = "message";

        },
        4000
    );

}


// =====================================
// LOAD ALL ALERTS
// =====================================

async function loadAlerts() {

    try {

        const response =
            await fetch("/api/alerts");


        const alerts =
            await response.json();


        if (!Array.isArray(alerts)) {

            console.error(
                "Invalid alert data:",
                alerts
            );

            return;

        }


        displayAlerts(alerts);

        updateStatistics(alerts);


    }

    catch (error) {

        console.error(
            "Error loading alerts:",
            error
        );

    }

}


// =====================================
// DISPLAY ALERTS
// =====================================

function displayAlerts(alerts) {

    const activeTable =
        document.getElementById(
            "activeAlertsTable"
        );


    const historyTable =
        document.getElementById(
            "alertHistoryTable"
        );


    activeTable.innerHTML = "";

    historyTable.innerHTML = "";


    const activeAlerts =
        alerts.filter(
            alert =>
                alert.status === "ACTIVE"
        );


    const triggeredAlerts =
        alerts.filter(
            alert =>
                alert.status === "TRIGGERED"
        );


    // =================================
    // ACTIVE ALERTS
    // =================================

    if (activeAlerts.length === 0) {

        activeTable.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="empty-message">

                    No active alerts.

                </td>

            </tr>

        `;

    }

    else {

        activeAlerts.forEach(
            alert => {

                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>
                        ${alert.id}
                    </td>

                    <td>
                        <strong>
                            ${escapeHtml(alert.symbol)}
                        </strong>
                    </td>

                    <td>
                        ₹${Number(
                            alert.target_price
                        ).toFixed(2)}
                    </td>

                    <td>
                        ${escapeHtml(
                            alert.condition_type
                        )}
                    </td>

                    <td>

                        <span
                            class="status-badge status-active">

                            ACTIVE

                        </span>

                    </td>

                    <td>

                        <button
                            class="delete-button"
                            onclick="deleteAlert(${alert.id})">

                            🗑 Delete

                        </button>

                    </td>

                `;


                activeTable.appendChild(row);

            }
        );

    }


    // =================================
    // ALERT HISTORY
    // =================================

    if (triggeredAlerts.length === 0) {

        historyTable.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="empty-message">

                    No triggered alerts yet.

                </td>

            </tr>

        `;

    }

    else {

        triggeredAlerts.forEach(
            alert => {

                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>
                        ${alert.id}
                    </td>

                    <td>
                        <strong>
                            ${escapeHtml(alert.symbol)}
                        </strong>
                    </td>

                    <td>
                        ₹${Number(
                            alert.target_price
                        ).toFixed(2)}
                    </td>

                    <td>
                        ${escapeHtml(
                            alert.condition_type
                        )}
                    </td>

                    <td>

                        <span
                            class="status-badge status-triggered">

                            TRIGGERED

                        </span>

                    </td>

                    <td>
                        ${
                            alert.triggered_at ||
                            "-"
                        }
                    </td>

                `;


                historyTable.appendChild(row);

            }
        );

    }

}


// =====================================
// UPDATE DASHBOARD STATISTICS
// =====================================

function updateStatistics(alerts) {

    const total =
        alerts.length;


    const active =
        alerts.filter(
            alert =>
                alert.status === "ACTIVE"
        ).length;


    const triggered =
        alerts.filter(
            alert =>
                alert.status === "TRIGGERED"
        ).length;


    document
        .getElementById("totalAlerts")
        .textContent = total;


    document
        .getElementById("activeAlertsCount")
        .textContent = active;


    document
        .getElementById("triggeredAlertsCount")
        .textContent = triggered;

}


// =====================================
// DELETE ALERT
// =====================================

async function deleteAlert(alertId) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this alert?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/alerts/${alertId}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (data.success) {

            loadAlerts();

        }

        else {

            alert(
                data.message ||
                "Could not delete alert."
            );

        }


    }

    catch (error) {

        console.error(error);

        alert(
            "Server error while deleting alert."
        );

    }

}


// =====================================
// GET STOCK PRICE
// =====================================

async function getStockPrice() {

    const symbol =
        document
            .getElementById("priceSymbol")
            .value
            .trim()
            .toUpperCase();


    const result =
        document.getElementById(
            "priceResult"
        );


    if (!symbol) {

        result.textContent =
            "Please enter a stock symbol.";

        return;

    }


    result.textContent =
        "⏳ Fetching stock price...";


    try {

        const response =
            await fetch(
                `/api/price/${encodeURIComponent(symbol)}`
            );


        const data =
            await response.json();


        if (data.success) {

            result.innerHTML = `

                <strong>
                    ${escapeHtml(data.symbol)}
                </strong>

                <br>

                <span class="live-price">

                    ₹${Number(
                        data.price
                    ).toFixed(2)}

                </span>

            `;

        }

        else {

            result.textContent =
                data.message ||
                "Could not fetch stock price.";

        }


    }

    catch (error) {

        console.error(error);

        result.textContent =
            "Error connecting to server.";

    }

}


// =====================================
// MARKET STATUS
// =====================================

async function loadMarketStatus() {

    const statusText =
        document.getElementById(
            "marketStatus"
        );


    const statusDot =
        document.getElementById(
            "statusDot"
        );


    try {

        const response =
            await fetch(
                "/api/market-status"
            );


        const data =
            await response.json();


        statusDot.className =
            "status-dot";


        if (data.status === "OPEN") {

            statusDot.classList.add("open");


            statusText.textContent =
                "🟢 MARKET OPEN | " +
                data.time;

        }

        else if (
            data.status === "PRE_OPEN"
        ) {

            statusDot.classList.add(
                "pre-open"
            );


            statusText.textContent =
                "🟡 PRE-OPEN SESSION | " +
                data.time;

        }

        else if (
            data.status === "WEEKEND"
        ) {

            statusDot.classList.add(
                "closed"
            );


            statusText.textContent =
                "🔴 MARKET CLOSED - WEEKEND | " +
                data.time;

        }

        else if (
            data.status === "HOLIDAY"
        ) {

            statusDot.classList.add(
                "closed"
            );


            statusText.textContent =
                "🔴 MARKET CLOSED - NSE HOLIDAY | " +
                data.time;

        }

        else {

            statusDot.classList.add(
                "closed"
            );


            statusText.textContent =
                "🔴 MARKET CLOSED | " +
                data.time;

        }

    }

    catch (error) {

        console.error(error);


        statusDot.className =
            "status-dot closed";


        statusText.textContent =
            "Unable to get market status.";

    }

}


// =====================================
// ESCAPE HTML
// =====================================

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// =====================================
// AUTOMATIC REFRESH
// =====================================

// Refresh alerts every 10 seconds

setInterval(
    loadAlerts,
    10000
);


// Refresh market status every 30 seconds

setInterval(
    loadMarketStatus,
    30000
);