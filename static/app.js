const ws = new WebSocket(`ws://${window.location.host}/ws`);

const els = {
    date: document.getElementById('current-date'),
    equity: document.getElementById('equity'),
    pnl: document.getElementById('pnl'),
    return: document.getElementById('return'),
    marketList: document.getElementById('market-list'),
    positionsList: document.getElementById('positions-list'),
    tradeLog: document.getElementById('trade-log'),
    btnStart: document.getElementById('btn-start'),
    btnStop: document.getElementById('btn-stop'),
    strategySelect: document.getElementById('strategy-select'),
    initialInvestment: document.getElementById('initial-investment'),
    brokerCharges: document.getElementById('broker-charges')
};

let initialCash = 100000.0;

// Event Listeners
els.btnStart.addEventListener('click', () => {
    const config = {
        initial_cash: parseFloat(els.initialInvestment.value),
        enable_broker_charges: els.brokerCharges.checked
    };

    // Update local initialCash for P&L calc
    initialCash = config.initial_cash;

    fetch('/api/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    })
        .then(res => res.json())
        .then(data => console.log(data));
});

els.btnStop.addEventListener('click', () => {
    fetch('/api/stop', { method: 'POST' })
        .then(res => res.json())
        .then(data => console.log(data));
});

els.strategySelect.addEventListener('change', (e) => {
    fetch('/api/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: e.target.value })
    })
        .then(res => res.json())
        .then(data => console.log(data));
});

// Poll status to update UI state
setInterval(() => {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            els.btnStart.disabled = data.is_running;
            els.btnStop.disabled = !data.is_running;
            els.strategySelect.value = data.active_strategy;
            els.strategySelect.disabled = data.is_running; // Disable strategy change while running
        });
}, 1000);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'update') {
        updateDashboard(data);
    } else if (data.type === 'finished') {
        console.log("Simulation Finished");
    }
};

function updateDashboard(data) {
    // Update Header
    // Show Date and Time (YYYY-MM-DD HH:MM)
    els.date.textContent = data.timestamp.slice(0, 16);
    els.equity.textContent = formatMoney(data.equity);

    const pnl = data.equity - initialCash;
    const returnPct = (pnl / initialCash) * 100;

    els.pnl.textContent = formatMoney(pnl);
    els.pnl.className = `value money ${pnl >= 0 ? 'positive' : 'negative'}`;

    els.return.textContent = `${returnPct.toFixed(2)}%`;
    els.return.className = `value ${returnPct >= 0 ? 'positive' : 'negative'}`;

    // Update Market Watch
    renderMarketList(data.prices);

    // Update Positions
    renderPositions(data.positions, data.prices);

    // Update Trades
    if (data.trades.length > 0) {
        renderTrades(data.trades);
    }
}

function renderMarketList(prices) {
    els.marketList.innerHTML = '';
    Object.entries(prices).forEach(([ticker, price]) => {
        const div = document.createElement('div');
        div.className = 'list-item';
        div.innerHTML = `
            <span class="ticker">${ticker}</span>
            <span class="price">$${price.toFixed(2)}</span>
            <span class="change">--</span>
        `;
        els.marketList.appendChild(div);
    });
}

function renderPositions(positions, prices) {
    els.positionsList.innerHTML = '';
    Object.entries(positions).forEach(([ticker, qty]) => {
        const price = prices[ticker] || 0;
        const value = qty * price;

        const div = document.createElement('div');
        div.className = 'list-item';
        div.innerHTML = `
            <span class="ticker">${ticker}</span>
            <span>${qty}</span>
            <span class="price">$${value.toFixed(2)}</span>
        `;
        els.positionsList.appendChild(div);
    });
}

function renderTrades(trades) {
    trades.forEach(trade => {
        const div = document.createElement('div');
        div.className = 'trade-item';
        div.innerHTML = `
            <span>${trade.timestamp.slice(0, 16)}</span>
            <span class="trade-action ${trade.action.toLowerCase()}">${trade.action}</span>
            <span>${trade.quantity} ${trade.ticker} @ ${trade.price.toFixed(2)}</span>
        `;
        els.tradeLog.prepend(div);
    });
}

function formatMoney(amount) {
    return '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}
