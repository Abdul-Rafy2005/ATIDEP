function drawRadar(selector, data) {
    d3.select(selector).select('svg').remove();

    const width = 420, height = 400;
    const margin = 65;
    const radius = Math.min(width, height) / 2 - margin;
    const levels = 4;

    const svg = d3.select(selector)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g')
        .attr('transform', `translate(${width/2}, ${height/2})`);

    const n = data.length;
    if (n === 0) return;

    const angleSlice = (Math.PI * 2) / n;
    const maxVal = 100;
    const rScale = d3.scaleLinear().domain([0, maxVal]).range([0, radius]);

    // Grid circles
    for (let i = 1; i <= levels; i++) {
        const r = radius * i / levels;
        g.append('circle')
            .attr('r', r)
            .attr('fill', 'none')
            .attr('stroke', '#e2e8f0')
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '3,3');

        g.append('text')
            .attr('x', 4)
            .attr('y', -r - 2)
            .attr('fill', '#94a3b8')
            .attr('font-size', '9px')
            .attr('font-family', 'monospace')
            .text(Math.round(maxVal * i / levels) + '%');
    }

    // Axis lines and labels
    data.forEach((d, i) => {
        const angle = angleSlice * i - Math.PI / 2;
        const x = radius * Math.cos(angle);
        const y = radius * Math.sin(angle);

        g.append('line')
            .attr('x1', 0).attr('y1', 0)
            .attr('x2', x).attr('y2', y)
            .attr('stroke', '#e2e8f0')
            .attr('stroke-width', 1);

        const labelRadius = radius + 22;
        const lx = labelRadius * Math.cos(angle);
        const ly = labelRadius * Math.sin(angle);

        const shortName = d.tactic_name.length > 15 ? d.tactic_name.substring(0, 13) + '..' : d.tactic_name;

        g.append('text')
            .attr('x', lx)
            .attr('y', ly)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', '#475569')
            .attr('font-size', '10px')
            .attr('font-weight', '600')
            .text(shortName);
    });

    // Coverage polygon area
    const line = d3.lineRadial()
        .radius(d => rScale(d.coverage_pct))
        .angle((d, i) => angleSlice * i)
        .curve(d3.curveCardinalClosed);

    g.append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'rgba(37, 99, 235, 0.12)')
        .attr('stroke', '#2563eb')
        .attr('stroke-width', 2);

    // Data points & tooltip
    const tooltip = d3.select('#radar-tooltip');

    data.forEach((d, i) => {
        const angle = angleSlice * i - Math.PI / 2;
        const x = rScale(d.coverage_pct) * Math.cos(angle);
        const y = rScale(d.coverage_pct) * Math.sin(angle);

        g.append('circle')
            .attr('cx', x).attr('cy', y)
            .attr('r', 4.5)
            .attr('fill', '#2563eb')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .on('mouseover', function(event) {
                d3.select(this).attr('r', 6).attr('fill', '#1d4ed8');
                tooltip.style('opacity', 1)
                    .html(`
                        <div class="font-bold text-white mb-0.5">${d.tactic_name}</div>
                        <div class="text-xs text-blue-200 font-mono">${d.covered} / ${d.total} techniques</div>
                        <div class="text-xs text-emerald-400 font-mono font-semibold">${d.coverage_pct}% coverage</div>
                    `);
            })
            .on('mousemove', function(event) {
                tooltip.style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 20) + 'px');
            })
            .on('mouseout', function() {
                d3.select(this).attr('r', 4.5).attr('fill', '#2563eb');
                tooltip.style('opacity', 0);
            });
    });
}
