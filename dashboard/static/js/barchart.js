function drawBarChart(selector, data) {
    d3.select(selector).select('svg').remove();

    const filtered = data.filter(d =>
        d.set === 3 && ['primary', 'baseline', 'exploratory'].includes(d.label)
    );

    if (filtered.length === 0) {
        d3.select(selector).append('div')
            .attr('class', 'text-slate-400 text-xs text-center py-12')
            .text('No Set 3 comparison data available');
        return;
    }

    const width = 450, height = 340;
    const margin = {top: 25, right: 20, bottom: 95, left: 45};
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const svg = d3.select(selector)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .attr('class', 'w-full h-full max-h-[340px]');

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
        .attr('stroke', '#f1f5f9')
        .attr('stroke-width', 1);

    g.select('.grid .domain').remove();

    // X axis
    g.append('g')
        .attr('transform', `translate(0, ${innerH})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('fill', '#475569')
        .attr('font-size', '11px')
        .attr('font-family', 'monospace')
        .attr('font-weight', '500')
        .attr('transform', 'rotate(-30)')
        .attr('text-anchor', 'end')
        .attr('dx', '-6px')
        .attr('dy', '6px');

    g.selectAll('.domain, .tick line').attr('stroke', '#cbd5e1');

    // Y axis
    g.append('g')
        .call(d3.axisLeft(y).ticks(6))
        .selectAll('text')
        .attr('fill', '#64748b')
        .attr('font-size', '10px')
        .attr('font-family', 'monospace');

    // Bar colors
    const colorMap = {
        'primary': '#2563eb',     // Blue
        'baseline': '#d97706',    // Amber
        'exploratory': '#9333ea'  // Purple
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
        .attr('fill', d => colorMap[d.label] || '#94a3b8')
        .attr('rx', 3);

    // Number label on top of bar
    g.selectAll('.bar-label')
        .data(filtered)
        .enter()
        .append('text')
        .attr('x', d => x(d.barLabel) + x.bandwidth() / 2)
        .attr('y', d => y(d.strict_pass) - 6)
        .attr('text-anchor', 'middle')
        .attr('fill', '#0f172a')
        .attr('font-size', '11px')
        .attr('font-family', 'monospace')
        .attr('font-weight', 'bold')
        .text(d => `${d.strict_pass}/60`);

    // Legend
    const legend = svg.append('g').attr('transform', `translate(${margin.left}, ${height - 15})`);
    [
        ['Primary (frozen)', '#2563eb'],
        ['Baseline (v1)', '#d97706'],
        ['Exploratory', '#9333ea']
    ].forEach(([label, color], i) => {
        const item = legend.append('g').attr('transform', `translate(${i * 130}, 0)`);
        item.append('rect').attr('width', 9).attr('height', 9).attr('fill', color).attr('rx', 2);
        item.append('text').attr('x', 14).attr('y', 8).attr('fill', '#475569').attr('font-size', '10px').attr('font-weight', '500').text(label);
    });
}
