function get_notams() {
    const icaoCodes = document
        .getElementById("icao-codes-for-request")
        .value.split(" ");
    const url = "/get_notams";
    const data = { icaoCodes: icaoCodes };
    const notams_list = [];

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then((data) => {
            const table = document.getElementById("notams-table"); // замените на id вашей таблицы

            Object.keys(data).forEach((key) => {
                data[key].forEach((value) => {
                    const row = table.insertRow();
                    row.innerHTML = `
                    <td id="CUVD">${key}</td>
                    <td id="name-NOTAM"></td>
                    <td id="start-NOTAM"></td>
                    <td id="end-NOTAM"></td>
                    <td id="text-NOTAM">${value}</td>`;
                });
            });
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

document.addEventListener("DOMContentLoaded", function () {
    document
        .getElementById("request-button")
        .addEventListener("click", get_notams);
});
