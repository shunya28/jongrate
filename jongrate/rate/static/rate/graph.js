const ctx = document.getElementById('chart').getContext('2d');

const data = {
    labels: ["1月", "2月", "3月", "4月", "5月", "6月", "7月"],
    datasets: [{
        label: "初めてのデータセット",
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: [0, 10, 5, 2, 20, 30, 45],
    },]
};

const options = {
    responsive: true,
    plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: '森レーティング'
        }
    }
};

const lineChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: options,
});