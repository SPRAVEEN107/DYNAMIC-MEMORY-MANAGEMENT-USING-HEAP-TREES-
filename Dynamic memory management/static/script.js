document.addEventListener('DOMContentLoaded', () => {
    const initButton = document.getElementById('init-memory');
    const allocateButton = document.getElementById('allocate');
    const deallocateButton = document.getElementById('deallocate');
    const deallocateMultipleButton = document.getElementById('deallocate-multiple');
    const memoryDisplay = document.getElementById('memory-display');
    let currentTotalSize = 1000;

    initButton.addEventListener('click', () => {
        const totalSizeInput = document.getElementById('total-size').value;
        currentTotalSize = parseInt(totalSizeInput);
        fetch('/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ total_size: currentTotalSize })
        })
        .then(response => response.json())
        .then(data => updateMemoryDisplay(data));
    });

    allocateButton.addEventListener('click', () => {
        const size = document.getElementById('alloc-size').value;
        const strategy = document.getElementById('strategy').value;
        fetch('/allocate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: parseInt(size), strategy: strategy })
        })
        .then(response => response.json())
        .then(data => updateMemoryDisplay(data));
    });

    deallocateButton.addEventListener('click', () => {
        const blockId = document.getElementById('dealloc-id').value;
        fetch('/deallocate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ block_id: blockId })
        })
        .then(response => response.json())
        .then(data => updateMemoryDisplay(data));
    });

    deallocateMultipleButton.addEventListener('click', () => {
        const ids = document.getElementById('dealloc-multiple-ids').value.split(',').map(id => id.trim());
        fetch('/deallocate_multiple', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ block_ids: ids.filter(id => id) })
        })
        .then(response => response.json())
        .then(data => updateMemoryDisplay(data));
    });

    function updateMemoryDisplay(data) {
        if (data.error) {
            alert(data.error);
            return;
        }
        memoryDisplay.innerHTML = '';
        const memoryBar = document.createElement('div');
        memoryBar.className = 'memory-bar';

        if (data && data.blocks) {
            const sortedBlocks = data.blocks.sort((a, b) => a.start_address - b.start_address);
            sortedBlocks.forEach(block => {
                const blockDiv = document.createElement('div');
                const statusClass = block.free ? 'free' : 'allocated';
                blockDiv.className = `block ${statusClass}`;
                blockDiv.style.width = `${(block.size / currentTotalSize) * 100}%`;
                blockDiv.textContent = `ID: ${block.id} (${block.size})`;
                memoryBar.appendChild(blockDiv);
            });
        }
        memoryDisplay.appendChild(memoryBar);
    }
});