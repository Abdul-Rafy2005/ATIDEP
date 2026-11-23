// MITRE ATT&CK Spider Web Radar Chart
// Matches exact geometry, concentric polygons, spokes, and dual-layer overlay from user reference image

const tacticIdMap = {
    'Reconnaissance': 'TA0043',
    'Resource Development': 'TA0042',
    'Initial Access': 'TA0001',
    'Execution': 'TA0002',
    'Persistence': 'TA0003',
    'Privilege Escalation': 'TA0004',
    'Defense Evasion': 'TA0005',
    'Credential Access': 'TA0006',
    'Discovery': 'TA0007',
    'Lateral Movement': 'TA0008',
    'Collection': 'TA0009',
    'Command and Control': 'TA0011',
    'Exfiltration': 'TA0010',
    'Impact': 'TA0040'
};

const adversaryIndex = {
    'TA0043': 75,
    'TA0042': 90,
    'TA0001': 75,
    'TA0002': 90,
    'TA0003': 15,
    'TA0004': 20,
    'TA0005': 95,
    'TA0006': 90,
    'TA0007': 85,
    'TA0008': 80,
    'TA0009': 10,
    'TA0011': 85,
    'TA0010': 15,
    'TA0040': 20
};

function drawRadar(selector, data) {
    d3.select(selector).select('svg').remove();

    const width = 400, height = 400;
    const margin = 50;
    const radius = Math.min(width, height) / 2 - margin;
    const levels = [0.25, 0.5, 0.75, 1.0];
    const n = data.length || 14;
    const angleSlice = (Math.PI * 2) / n;

    const svg = d3.select(selector)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .attr('class', 'w-full h-full max-h-[350px] select-none');

    const g = svg.append('g')
        .attr('transform', `translate(${width/2}, ${height/2})`);

    // 1. Concentric 14-sided polygon web lines (True spider web, not circles!)
    levels.forEach((level) => {
        const r = radius * level;
        const ringPoints = [];
        for (let i = 0; i < n; i++) {
            const angle = angleSlice * i - Math.PI / 2;
            ringPoints.push([r * Math.cos(angle), r * Math.sin(angle)]);
        }
        g.append('polygon')
            .attr('points', ringPoints.map(p => p.join(',')).join(' '))
            .attr('fill', 'none')
            .attr('stroke', '#e2e8f0')
            .attr('stroke-width', 1);

        // Center axis scale text along the top vertical spoke
        if (level < 1.0) {
            g.append('text')
                .attr('x', 4)
                .attr('y', -r - 2)
                .attr('fill', '#94a3b8')
                .attr('font-size', '9px')
                .attr('font-family', 'monospace')
                .text(Math.round(level * 100) + '%');
        }
    });

    g.append('text')
        .attr('x', 4)
        .attr('y', -2)
        .attr('fill', '#94a3b8')
        .attr('font-size', '9px')
        .attr('font-family', 'monospace')
        .text('0%');

    // 2. Radial spokes from center to each vertex
    for (let i = 0; i < n; i++) {
        const angle = angleSlice * i - Math.PI / 2;
        const x2 = radius * Math.cos(angle);
        const y2 = radius * Math.sin(angle);
        g.append('line')
            .attr('x1', 0).attr('y1', 0)
            .attr('x2', x2).attr('y2', y2)
            .attr('stroke', '#e2e8f0')
            .attr('stroke-width', 1);
    }

    // 3. Perimeter Tactic ID Labels (TA0043, TA0042, etc.)
    data.forEach((d, i) => {
        const tid = tacticIdMap[d.tactic_name] || `TA00${i+1}`;
        d.tactic_id = tid;
        const angle = angleSlice * i - Math.PI / 2;
        const lx = (radius + 22) * Math.cos(angle);
        const ly = (radius + 22) * Math.sin(angle);

        g.append('text')
            .attr('x', lx)
            .attr('y', ly)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', '#64748b')
            .attr('font-size', '10px')
            .attr('font-family', 'monospace')
            .attr('font-weight', '600')
            .text(tid);
    });

    // 4. Adversary Polygon (Red / Rose layer with transparency)
    const advPoints = [];
    data.forEach((d, i) => {
        const advVal = adversaryIndex[d.tactic_id] || 40;
        const r = (radius * advVal) / 100;
        const angle = angleSlice * i - Math.PI / 2;
        advPoints.push([r * Math.cos(angle), r * Math.sin(angle)]);
    });

    g.append('polygon')
        .attr('points', advPoints.map(p => p.join(',')).join(' '))
        .attr('fill', 'rgba(225, 29, 72, 0.22)')
        .attr('stroke', '#e11d48')
        .attr('stroke-width', 1.5);

    // 5. Coverage Polygon (Blue / Indigo layer with transparency)
    const covPoints = [];
    data.forEach((d, i) => {
        const r = (radius * (d.coverage_pct || 50)) / 100;
        const angle = angleSlice * i - Math.PI / 2;
        covPoints.push([r * Math.cos(angle), r * Math.sin(angle)]);
    });

    g.append('polygon')
        .attr('points', covPoints.map(p => p.join(',')).join(' '))
        .attr('fill', 'rgba(79, 70, 229, 0.25)')
        .attr('stroke', '#4f46e5')
        .attr('stroke-width', 1.5);

    // 6. Interactive Nodes & Tooltip
    const tooltip = d3.select('#radar-tooltip');

    data.forEach((d, i) => {
        const r = (radius * (d.coverage_pct || 50)) / 100;
        const angle = angleSlice * i - Math.PI / 2;
        const x = r * Math.cos(angle);
        const y = r * Math.sin(angle);

        g.append('circle')
            .attr('cx', x).attr('cy', y)
            .attr('r', 4)
            .attr('fill', '#4f46e5')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 1.5)
            .style('cursor', 'pointer')
            .on('mouseover', function(event) {
                d3.select(this).attr('r', 6).attr('fill', '#1e1b4b');
                tooltip.style('opacity', 1)
                    .html(`
                        <div class="font-bold text-white mb-0.5">${d.tactic_id} - ${d.tactic_name}</div>
                        <div class="text-xs text-blue-200 font-mono">Rule Coverage: ${d.coverage_pct}% (${d.covered || 0}/${d.total || 0} tech)</div>
                        <div class="text-xs text-rose-300 font-mono">Adversary Activity: ${adversaryIndex[d.tactic_id] || 40}%</div>
                    `);
            })
            .on('mousemove', function(event) {
                tooltip.style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 20) + 'px');
            })
            .on('mouseout', function() {
                d3.select(this).attr('r', 4).attr('fill', '#4f46e5');
                tooltip.style('opacity', 0);
            });
    });
}
