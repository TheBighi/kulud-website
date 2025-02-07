document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("expense-form");
    const expenseList = document.getElementById("expense-list");

    const today = new Date().toISOString().split('T')[0]; 
    document.getElementById("expense-date").value = today;

    function fetchExpenses() {
        fetch('http://127.0.0.1:5000/get_expenses')
            .then(response => response.json())
            .then(data => {
                expenseList.innerHTML = "";
                data.forEach(expense => {
                    const listItem = document.createElement("li");
                    listItem.innerHTML = `${expense.name} - ${expense.date} - €${expense.amount} 
                        <button class="delete-btn" data-id="${expense.id}">❌</button>`;
                    expenseList.appendChild(listItem);
                });

                // add delete
                document.querySelectorAll('.delete-btn').forEach(button => {
                    button.addEventListener('click', function () {
                        const expenseId = this.getAttribute('data-id');
                        deleteExpense(expenseId);
                    });
                });
            })
            .catch(error => console.error('Error fetching expenses:', error));
    }
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("expense-name").value;
        const date = document.getElementById("expense-date").value;
        const amount = document.getElementById("expense-amount").value;

        if (name && date && amount) {
            fetch('http://127.0.0.1:5000/add_expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, date, amount })
            })
            .then(response => response.json())
            .then(() => {
                fetchExpenses();
                form.reset();
            })
            .catch(error => console.error('Error adding expense:', error));
        }
    });

    function deleteExpense(expenseId) {
        fetch(`http://127.0.0.1:5000/delete_expense/${expenseId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(() => {
            fetchExpenses();
        })
        .catch(error => console.error('Error deleting expense:', error));
    }

    fetchExpenses(); // load 
});
