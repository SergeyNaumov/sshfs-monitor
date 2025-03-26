document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.querySelector("#connections-table tbody");
    const searchInput = document.getElementById("search-input");

    let allConnections = [];

    // Функция для обновления таблицы
    async function updateTable() {
        try {
            const response = await fetch("/connections");
            const connections = await response.json();

            console.log("Загруженные соединения:", connections); // Отладка: вывод загруженных данных

            allConnections = Object.entries(connections); // Сохраняем все соединения
            applyFilter(); // Применяем текущий фильтр
        } catch (error) {
            console.error("Ошибка при загрузке данных:", error);
        }
    }

    // Функция для отрисовки таблицы
    function renderTable(data) {
        tableBody.innerHTML = ""; // Очищаем таблицу

        data.forEach(([name, info]) => {
            const row = document.createElement("tr");

            // Имя соединения
            const nameCell = document.createElement("td");
            nameCell.textContent = name;
            row.appendChild(nameCell);

            // Точка монтирования
            const mountPointCell = document.createElement("td");
            mountPointCell.textContent = info.mount_point;
            row.appendChild(mountPointCell);

            // Состояние
            const statusCell = document.createElement("td");
            statusCell.textContent = info.mounted ? "Смонтировано" : "Не смонтировано";
            statusCell.style.color = info.mounted ? "green" : "red";
            row.appendChild(statusCell);

            // Кнопки действий
            const actionsCell = document.createElement("td");
            const mountButton = document.createElement("button");
            mountButton.textContent = "Монтировать";
            mountButton.disabled = info.mounted;
            mountButton.onclick = () => mountConnection(name);

            const umountButton = document.createElement("button");
            umountButton.textContent = "Размонтировать";
            umountButton.disabled = !info.mounted;
            umountButton.onclick = () => unmountConnection(name);

            actionsCell.appendChild(mountButton);
            actionsCell.appendChild(umountButton);
            row.appendChild(actionsCell);

            tableBody.appendChild(row);
        });
    }

    // Функция для применения фильтра
    function applyFilter() {
        const query = searchInput.value.toLowerCase();
        if (!query) {
            renderTable(allConnections); // Если запрос пустой, показываем все соединения
            return;
        }

        // Фильтруем соединения: ищем вхождение текста в любом месте имени
        const filtered = allConnections.filter(([name]) => {
            const match = name.toLowerCase().includes(query);

            return match;
        });

        renderTable(filtered);
    }

    // Функция для фильтрации соединений
    async function filterConnections() {
        applyFilter();
    }

    // Привязываем функцию к событию oninput
    searchInput.oninput = filterConnections;

    // Функция для монтирования
    async function mountConnection(name) {
        try {
            await fetch(`/connections/${name}/mount`, { method: "POST" });
            updateTable(); // Обновляем таблицу с учётом фильтра
        } catch (error) {
            console.error("Ошибка при монтировании:", error);
        }
    }

    // Функция для размонтирования
    async function unmountConnection(name) {
        try {
            await fetch(`/connections/${name}/umount`, { method: "POST" });
            updateTable(); // Обновляем таблицу с учётом фильтра
        } catch (error) {
            console.error("Ошибка при размонтировании:", error);
        }
    }

    // Обновляем таблицу при загрузке страницы
    updateTable();
});