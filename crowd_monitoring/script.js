document.addEventListener('DOMContentLoaded', () => {
    const roomCard = document.getElementById('room-1');
    const statusBadge = document.getElementById('status-badge');
    const visualIndicator = document.getElementById('visual-indicator');
    const countDisplay = document.getElementById('count-display');
    const statusText = document.getElementById('status-text');

    function updateDashboard() {
        fetch('http://localhost:5000/data')
            .then(response => response.json())
            .then(data => {
                const count = data.count;
                const status = data.status;

                // Update text
                countDisplay.textContent = count;
                statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                statusBadge.textContent = status.toUpperCase();

                // Reset classes
                roomCard.classList.remove('green', 'orange', 'red');

                // Add new class
                roomCard.classList.add(status);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                statusBadge.textContent = "OFFLINE";
                roomCard.classList.remove('green', 'orange', 'red');
            });
    }

    // Poll every 1 second
    setInterval(updateDashboard, 1000);

    // Initial call
    updateDashboard();
});
