export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function formatDecimal(value, digits = 3) {
  return Number(value).toFixed(digits).replace(/0+$/, "").replace(/\.$/, "");
}

export function formatPercent(value, digits = 1) {
  return `${(value * 100).toFixed(digits).replace(/\.0$/, "")}%`;
}

export function button(label, action, extra = {}) {
  const attrs = Object.entries(extra)
    .map(([key, value]) => `data-${key}="${escapeHtml(value)}"`)
    .join(" ");
  return `<button class="button" data-action="${escapeHtml(action)}" ${attrs}>${escapeHtml(label)}</button>`;
}

export function ghostButton(label, action, extra = {}) {
  const attrs = Object.entries(extra)
    .map(([key, value]) => `data-${key}="${escapeHtml(value)}"`)
    .join(" ");
  return `<button class="button button-ghost" data-action="${escapeHtml(action)}" ${attrs}>${escapeHtml(label)}</button>`;
}

export function metricCard(label, value, note = "") {
  return `
    <div class="metric-card">
      <span class="metric-label">${escapeHtml(label)}</span>
      <strong class="metric-value">${escapeHtml(value)}</strong>
      ${note ? `<span class="metric-note">${escapeHtml(note)}</span>` : ""}
    </div>
  `;
}

export function shell({ themeClass, homeHtml, contentHtml }) {
  return `
    <main class="shell ${escapeHtml(themeClass)}">
      ${homeHtml}
      ${contentHtml}
    </main>
  `;
}

export function topBar({ title, subtitle = "", showPathwayBadge = "" }) {
  return `
    <header class="topbar">
      <div>
        <p class="topbar-kicker">Linguistics Project Demo</p>
        <h1>${escapeHtml(title)}</h1>
        ${subtitle ? `<p class="topbar-subtitle">${escapeHtml(subtitle)}</p>` : ""}
      </div>
      ${showPathwayBadge ? `<div class="pathway-badge">${escapeHtml(showPathwayBadge)}</div>` : ""}
    </header>
  `;
}

export function pathwayFrame({
  title,
  eyebrow,
  progressLabel,
  controlsHtml,
  heroHtml,
  bodyHtml,
}) {
  return `
    ${topBar({ title, subtitle: progressLabel, showPathwayBadge: eyebrow })}
    <section class="pathway-shell">
      <aside class="pathway-controls">
        ${controlsHtml}
      </aside>
      <div class="pathway-main">
        ${heroHtml}
        ${bodyHtml}
      </div>
    </section>
  `;
}

export function pathwayControls({ canBack, pathwayId }) {
  return `
    <div class="control-card">
      <span class="control-label">Navigate</span>
      <div class="control-stack">
        ${ghostButton("Home", "go-home")}
        ${
          canBack
            ? ghostButton("Back", "go-back", { pathway: pathwayId })
            : `<button class="button button-ghost" disabled>Back</button>`
        }
        ${ghostButton("Restart", "restart-pathway", { pathway: pathwayId })}
      </div>
    </div>
  `;
}

export function choiceCard({
  label,
  body,
  selected = false,
  disabled = false,
  disabledLabel = "",
  action,
  extra = {},
}) {
  const attrs = Object.entries(extra)
    .map(([key, value]) => `data-${key}="${escapeHtml(value)}"`)
    .join(" ");
  if (disabled) {
    return `
      <button
        class="choice-card choice-card-disabled"
        disabled
      >
        <strong>${escapeHtml(label)}</strong>
        ${disabledLabel ? `<span class="disabled-badge">${escapeHtml(disabledLabel)}</span>` : ""}
        ${body ? `<span>${escapeHtml(body)}</span>` : ""}
      </button>
    `;
  }
  return `
    <button
      class="choice-card ${selected ? "choice-card-selected" : ""}"
      data-action="${escapeHtml(action)}"
      ${attrs}
    >
      <strong>${escapeHtml(label)}</strong>
      ${body ? `<span>${escapeHtml(body)}</span>` : ""}
    </button>
  `;
}

export function tableCard(title, subtitle, innerHtml) {
  return `
    <section class="panel-card">
      <div class="panel-header">
        <h3>${escapeHtml(title)}</h3>
        ${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ""}
      </div>
      ${innerHtml}
    </section>
  `;
}

export function progressPill(text) {
  return `<span class="progress-pill">${escapeHtml(text)}</span>`;
}
