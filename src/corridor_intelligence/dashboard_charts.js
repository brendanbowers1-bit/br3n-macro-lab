  const C = {
    paper: "#F7F4EC",
    green: "#7DDC8A",
    rose: "#FF6B6B",
    teal: "#2DD4BF",
    cyan: "#6EE7F9",
    blue: "#7AA7FF",
    silver: "#CBD3DD",
    slate: "rgba(247, 244, 236, 0.55)",
    grid: "rgba(247, 244, 236, 0.08)"
  };

  const monthLabels = (CORRIDOR.series && CORRIDOR.series.month_labels) || [];
  const remittances = (CORRIDOR.series && CORRIDOR.series.remittance_usd_millions) || [];
  if (!remittances.length) return;

  const n = remittances.length - 1;
  const latest = remittances[n];
  const prev = remittances[n - 1];
  const nov2024 = remittances[10];
  const yoyAbs = latest - nov2024;
  const yoyPct = (yoyAbs / nov2024) * 100;
  const momAbs = latest - prev;
  const momPct = (momAbs / prev) * 100;
  const ytd2025 = remittances.slice(12, 23).reduce((a, b) => a + b, 0);
  const peakVal = Math.max(...remittances);
  const troughVal = Math.min(...remittances);
  const peakIdx = remittances.indexOf(peakVal);
  const troughIdx = remittances.indexOf(troughVal);

  const momDeltas = remittances.map((v, i) => (i === 0 ? null : v - remittances[i - 1]));
  const momLabels = monthLabels.slice(1);
  const momValues = momDeltas.slice(1);
  const momColors = momValues.map(v => v > 0 ? "rgba(125, 220, 138, 0.72)" : v < 0 ? "rgba(255, 107, 107, 0.72)" : "rgba(203, 211, 221, 0.45)");

  const yoyGapLabels = monthLabels.slice(12, 23);
  const yoyGapValues = yoyGapLabels.map((_, i) => remittances[12 + i] - remittances[i]);
  const yoyGapColors = yoyGapValues.map(v => v >= 0 ? "rgba(125, 220, 138, 0.65)" : "rgba(255, 107, 107, 0.65)");

  const pointColors = remittances.map((v, i) => {
    if (i === peakIdx) return C.green;
    if (i === troughIdx) return C.rose;
    if (i === 0) return C.cyan;
    const d = v - remittances[i - 1];
    if (d > 0) return C.teal;
    if (d < 0) return C.rose;
    return C.silver;
  });
  const pointRadii = remittances.map((_, i) => (i === peakIdx || i === troughIdx || i === n ? 6 : 3));

  function fmt(n, dec) {
    return n.toLocaleString("en-US", { maximumFractionDigits: dec || 0, minimumFractionDigits: dec || 0 });
  }

  function countUp(el, target, duration, decimals, prefix, suffix) {
    const start = performance.now();
    const from = 0;
    function frame(now) {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      const val = from + (target - from) * ease;
      el.textContent = (prefix || "") + fmt(val, decimals) + (suffix || "");
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function animateInsights() {
    document.querySelectorAll("[data-count]").forEach(el => {
      const target = parseFloat(el.getAttribute("data-count"));
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const suffix = el.getAttribute("data-suffix") || "";
      const prefix = target > 0 && el.id === "insightYoyPct" ? "+" : (target < 0 && el.id === "insightYoyPct" ? "" : "");
      countUp(el, target, 1400, decimals, prefix, suffix);
    });
    const yoyAbsEl = document.getElementById("insightYoyAbs");
    if (yoyAbsEl) {
      const sign = yoyAbs >= 0 ? "+" : "−";
      yoyAbsEl.textContent = sign + fmt(Math.abs(yoyAbs)) + "M vs Nov 2024";
      yoyAbsEl.className = "insight-delta " + (yoyAbs >= 0 ? "positive" : "negative");
    }
  }

  function buildStory() {
    const momWord = Math.abs(momPct) < 0.5 ? "flat" : (momPct > 0 ? "accelerating" : "easing");
    const yoyWord = yoyPct >= 0 ? "above" : "below";
    const pace = latest < peakVal * 0.92 ? "cooled from 2024 highs" : "holding elevated levels";
    return (
      "Corridor flows peaked at <strong>" + fmt(peakVal) + "M</strong> in " + monthLabels[peakIdx] +
      ". The latest reading (<strong>" + fmt(latest) + "M</strong>, " + monthLabels[n] + ") sits <strong>" +
      Math.abs(yoyPct).toFixed(1) + "% " + yoyWord + "</strong> the same month last year and looks <strong>" +
      momWord + "</strong> month-over-month (" + (momAbs >= 0 ? "+" : "") + fmt(momAbs) + "M). " +
      "2025 YTD (Jan–Nov) totals <strong>" + fmt(ytd2025) + "M</strong>, suggesting the corridor has <strong>" +
      pace + "</strong> while remaining structurally large. Trough in starter series: <strong>" +
      fmt(troughVal) + "M</strong> (" + monthLabels[troughIdx] + ")."
    );
  }

  const storyEl = document.getElementById("corridorStory");
  if (storyEl) storyEl.innerHTML = buildStory();

  let insightsAnimated = false;
  function triggerInsights() {
    if (insightsAnimated) return;
    insightsAnimated = true;
    animateInsights();
  }

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      if (entry.target.id === "insightStrip" || entry.target.classList.contains("insight-card")) {
        triggerInsights();
      }
      io.unobserve(entry.target);
    });
  }, { threshold: 0.2 });

  document.querySelectorAll("[data-animate]").forEach(el => io.observe(el));
  io.observe(document.getElementById("insightStrip"));

  const peakTroughPlugin = {
    id: "peakTroughLabels",
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      [peakIdx, troughIdx, n].forEach(i => {
        const pt = meta.data[i];
        if (!pt) return;
        const label = i === peakIdx ? "PEAK" : (i === troughIdx ? "TROUGH" : "LATEST");
        const color = i === peakIdx ? C.green : (i === troughIdx ? C.rose : C.cyan);
        ctx.save();
        ctx.fillStyle = color;
        ctx.font = "600 10px Inter, Helvetica, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(label, pt.x, pt.y - 14);
        ctx.restore();
      });
    }
  };

  const monthLabels = (CORRIDOR.series && CORRIDOR.series.month_labels) || [];
  const remittances = (CORRIDOR.series && CORRIDOR.series.remittance_usd_millions) || [];
  if (!remittances.length) return;

  const n = remittances.length - 1;
  const latest = remittances[n];
  const prev = remittances[n - 1];
  const nov2024 = remittances[10];
  const yoyAbs = latest - nov2024;
  const yoyPct = (yoyAbs / nov2024) * 100;
  const momAbs = latest - prev;
  const momPct = (momAbs / prev) * 100;
  const ytd2025 = remittances.slice(12, 23).reduce((a, b) => a + b, 0);
  const peakVal = Math.max(...remittances);
  const troughVal = Math.min(...remittances);
  const peakIdx = remittances.indexOf(peakVal);
  const troughIdx = remittances.indexOf(troughVal);

  const momDeltas = remittances.map((v, i) => (i === 0 ? null : v - remittances[i - 1]));
  const momLabels = monthLabels.slice(1);
  const momValues = momDeltas.slice(1);
  const momColors = momValues.map(v => v > 0 ? "rgba(125, 220, 138, 0.72)" : v < 0 ? "rgba(255, 107, 107, 0.72)" : "rgba(203, 211, 221, 0.45)");

  const yoyGapLabels = monthLabels.slice(12, 23);
  const yoyGapValues = yoyGapLabels.map((_, i) => remittances[12 + i] - remittances[i]);
  const yoyGapColors = yoyGapValues.map(v => v >= 0 ? "rgba(125, 220, 138, 0.65)" : "rgba(255, 107, 107, 0.65)");

  const pointColors = remittances.map((v, i) => {
    if (i === peakIdx) return C.green;
    if (i === troughIdx) return C.rose;
    if (i === 0) return C.cyan;
    const d = v - remittances[i - 1];
    if (d > 0) return C.teal;
    if (d < 0) return C.rose;
    return C.silver;
  });
  const pointRadii = remittances.map((_, i) => (i === peakIdx || i === troughIdx || i === n ? 6 : 3));

  function fmt(n, dec) {
    return n.toLocaleString("en-US", { maximumFractionDigits: dec || 0, minimumFractionDigits: dec || 0 });
  }

  function countUp(el, target, duration, decimals, prefix, suffix) {
    const start = performance.now();
    const from = 0;
    function frame(now) {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      const val = from + (target - from) * ease;
      el.textContent = (prefix || "") + fmt(val, decimals) + (suffix || "");
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function animateInsights() {
    document.querySelectorAll("[data-count]").forEach(el => {
      const target = parseFloat(el.getAttribute("data-count"));
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const suffix = el.getAttribute("data-suffix") || "";
      const prefix = target > 0 && el.id === "insightYoyPct" ? "+" : (target < 0 && el.id === "insightYoyPct" ? "" : "");
      countUp(el, target, 1400, decimals, prefix, suffix);
    });
    const yoyAbsEl = document.getElementById("insightYoyAbs");
    if (yoyAbsEl) {
      const sign = yoyAbs >= 0 ? "+" : "−";
      yoyAbsEl.textContent = sign + fmt(Math.abs(yoyAbs)) + "M vs Nov 2024";
      yoyAbsEl.className = "insight-delta " + (yoyAbs >= 0 ? "positive" : "negative");
    }
  }

  function buildStory() {
    const momWord = Math.abs(momPct) < 0.5 ? "flat" : (momPct > 0 ? "accelerating" : "easing");
    const yoyWord = yoyPct >= 0 ? "above" : "below";
    const pace = latest < peakVal * 0.92 ? "cooled from 2024 highs" : "holding elevated levels";
    return (
      "Corridor flows peaked at <strong>" + fmt(peakVal) + "M</strong> in " + monthLabels[peakIdx] +
      ". The latest reading (<strong>" + fmt(latest) + "M</strong>, " + monthLabels[n] + ") sits <strong>" +
      Math.abs(yoyPct).toFixed(1) + "% " + yoyWord + "</strong> the same month last year and looks <strong>" +
      momWord + "</strong> month-over-month (" + (momAbs >= 0 ? "+" : "") + fmt(momAbs) + "M). " +
      "2025 YTD (Jan–Nov) totals <strong>" + fmt(ytd2025) + "M</strong>, suggesting the corridor has <strong>" +
      pace + "</strong> while remaining structurally large. Trough in starter series: <strong>" +
      fmt(troughVal) + "M</strong> (" + monthLabels[troughIdx] + ")."
    );
  }

  const storyEl = document.getElementById("corridorStory");
  if (storyEl) storyEl.innerHTML = buildStory();

  let insightsAnimated = false;
  function triggerInsights() {
    if (insightsAnimated) return;
    insightsAnimated = true;
    animateInsights();
  }

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      if (entry.target.id === "insightStrip" || entry.target.classList.contains("insight-card")) {
        triggerInsights();
      }
      io.unobserve(entry.target);
    });
  }, { threshold: 0.2 });

  document.querySelectorAll("[data-animate]").forEach(el => io.observe(el));
  io.observe(document.getElementById("insightStrip"));

  const peakTroughPlugin = {
    id: "peakTroughLabels",
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      [peakIdx, troughIdx, n].forEach(i => {
        const pt = meta.data[i];
        if (!pt) return;
        const label = i === peakIdx ? "PEAK" : (i === troughIdx ? "TROUGH" : "LATEST");
        const color = i === peakIdx ? C.green : (i === troughIdx ? C.rose : C.cyan);
        ctx.save();
        ctx.fillStyle = color;
        ctx.font = "600 10px Inter, Helvetica, sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(label, pt.x, pt.y - 14);
        ctx.restore();
      });
    }
  };

  const baseScales = {
    x: {
      ticks: { color: C.slate, maxRotation: 45, minRotation: 45, font: { size: 10 } },
      grid: { color: C.grid },
      title: { display: true, text: "Month", color: "rgba(247,244,236,0.45)", font: { size: 11 } }
    },
    y: {
      ticks: { color: C.slate, font: { size: 11 } },
      grid: { color: C.grid },
      title: { display: true, text: "USD millions", color: "rgba(247,244,236,0.45)", font: { size: 11 } }
    }
  };

  const basePlugins = {
    legend: { display: false },
    tooltip: {
      backgroundColor: "rgba(5, 7, 10, 0.94)",
      borderColor: "rgba(247, 244, 236, 0.18)",
      borderWidth: 1,
      titleColor: C.paper,
      bodyColor: "rgba(247, 244, 236, 0.78)",
      callbacks: {
        label(ctx) {
          let line = ctx.dataset.label + ": " + fmt(ctx.parsed.y) + "M";
          if (ctx.chart.canvas.id === "momChart") return "MoM: " + (ctx.parsed.y >= 0 ? "+" : "") + fmt(ctx.parsed.y) + "M";
          if (ctx.chart.canvas.id === "yoyGapChart") return "YoY gap: " + (ctx.parsed.y >= 0 ? "+" : "") + fmt(ctx.parsed.y) + "M";
          return line;
        }
      }
    }
  };

  const anim = { duration: 1400, easing: "easeOutQuart" };

  new Chart(document.getElementById("remittanceChart"), {
    type: "line",
    data: {
      labels: monthLabels,
      datasets: [{
        label: "Monthly remittances",
        data: remittances,
        borderColor: C.cyan,
        backgroundColor: "rgba(110, 231, 249, 0.06)",
        borderWidth: 2.5,
        pointRadius: pointRadii,
        pointHoverRadius: 8,
        pointBackgroundColor: pointColors,
        pointBorderColor: "rgba(5, 7, 10, 0.85)",
        pointBorderWidth: 1.5,
        tension: 0.28,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: baseScales
    },
    plugins: [peakTroughPlugin]
  });

  new Chart(document.getElementById("momChart"), {
    type: "bar",
    data: {
      labels: momLabels,
      datasets: [{
        label: "MoM change",
        data: momValues,
        backgroundColor: momColors,
        borderColor: momColors.map(c => c.replace("0.72", "1").replace("0.45", "0.8")),
        borderWidth: 1,
        borderRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: {
        ...baseScales,
        y: { ...baseScales.y, title: { ...baseScales.y.title, text: "USD millions change" } }
      }
    }
  });

  new Chart(document.getElementById("yoyGapChart"), {
    type: "bar",
    data: {
      labels: yoyGapLabels,
      datasets: [{
        label: "YoY gap",
        data: yoyGapValues,
        backgroundColor: yoyGapColors,
        borderColor: yoyGapColors.map(c => c.replace("0.65", "1")),
        borderWidth: 1,
        borderRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: {
        ...baseScales,
        y: { ...baseScales.y, title: { ...baseScales.y.title, text: "2025 minus 2024 (USD millions)" } }
      }
    }
  });

  const rollingLabels = [];
  const rollingValues = [];
  for (let i = 11; i < remittances.length; i++) {
    let sum = 0;
    for (let j = i - 11; j <= i; j++) sum += remittances[j];
    rollingLabels.push(monthLabels[i]);
    rollingValues.push(sum);
  }

  new Chart(document.getElementById("rollingChart"), {
    type: "line",
    data: {
      labels: rollingLabels,
      datasets: [{
        label: "12-month rolling total",
        data: rollingValues,
        borderColor: C.blue,
        backgroundColor: "rgba(122, 167, 255, 0.08)",
        borderWidth: 2,
        pointRadius: 2,
        pointBackgroundColor: C.blue,
        tension: 0.25,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: anim,
      plugins: basePlugins,
      scales: baseScales
    }
  });
