function drawBarChart(selector, data) {
    d3.select(selector).select('svg').remove();

    // Filter to set 3 runs only, and only primary/baseline/exploratory
    const filtered = data.filter(d =>
        d.set === 3 && ['primary', 'baseline', 'exploratory'].includes(d.label)
    );

    if (filtered.length === 0) {
        d3.select(selector).append('div')
            .attr('class', 'text-slate-500 text-xs text-center py-12')
            .text('No Set 3 comparison data available');
        return;
    }

    const width = 450, height = 340;
    const margin = {top: 25, right: 20, bottom: 95, left: 45};
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const svg = d3.select(selector)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Format display labels
    filtered.forEach(d => {
        const shortModel = d.model.replace('qwen2.5-coder:', '');
        d.barLabel = `${shortModel} (${d.prompt})`;
    });

    const x = d3.scaleBand()
        .domain(filtered.map(d => d.barLabel))
        .range([0, innerW])
        .padding(0.35);

    const y = d3.scaleLinear()
        .domain([0, 60])
        .range([innerH, 0]);

    // Gridlines
    g.append('g')
        .attr('class', 'grid')
        .call(d3.axisLeft(y).ticks(6).tickSize(-innerW).tickFormat(''))
        .selectAll('line')
        .attr('stroke', '#334155')
        .attr('stroke-width', 0.5)
        .attr('stroke-dasharray', '2,2');

    g.select('.grid .domain').remove();

    // X axis
    g.append('g')
        .attr('transform', `translate(0, ${innerH})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('fill', '#94a3b8')
        .attr('font-size', '11px')
        .attr('font-family', 'monospace')
        .attr('transform', 'rotate(-30)')
        .attr('text-anchor', 'end')
        .attr('dx', '-6px')
        .attr('dy', '6px');

    g.selectAll('.domain, .tick line').attr('stroke', '#334155');

    // Y axis
    g.append('g')
        .call(d3.axisLeft(y).ticks(6))
        .selectAll('text')
        .attr('fill', '#94a3b8')
        .attr('font-size', '10px')
        .attr('font-family', 'monospace');

    // Bar colors
    const colorMap = {
        'primary': '#3b82f6',
        'baseline': '#f59e0b',
        'exploratory': '#a855f7'
    };

    // Bars
    g.selectAll('.bar')
        .data(filtered)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.barLabel))
        .attr('y', d => y(d.strict_pass))
        .attr('width', x.bandwidth())
        .attr('height', d => innerH - y(d.strict_pass))
        .attr('fill', d => colorMap[d.label] || '#64748b')
        .attr('rx', 3);

    // Number label on top of bar
    g.selectAll('.bar-label')
        .data(filtered)
        .enter()
        .append('text')
        .attr('x', d => x(d.barLabel) + x.bandwidth() / 2)
        .attr('y', d => y(d.strict_pass) - 6)
        .attr('text-anchor', 'middle')
        .attr('fill', '#e2e8f0')
        .attr('font-size', '11px')
        .attr('font-family', 'monospace')
        .attr('font-weight', 'bold')
        .text(d => `${d.strict_pass}/60`);

    // Legend
    const legend = svg.append('g').attr('transform', `translate(${margin.left}, ${height - 15})`);
    [
        ['Primary (frozen)', '#3b82f6'],
        ['Baseline (v1)', '#f59e0b'],
        ['Exploratory', '#a855f7']
    ].forEach(([label, color], i) => {
        const item = legend.append('g').attr('transform', `translate(${i * 130}, 0)`);
        item.append('rect').attr('width', 9).attr('height', 9).attr('fill', color).attr('rx', 2);
        item.append('text').attr('x', 14).attr('y', 8).attr('fill', '#94a3b8').attr('font-size', '10px').text(label);
    });
}

