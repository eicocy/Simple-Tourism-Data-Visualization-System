<template>
  <article class="portfolio-card gauge-card">
    <div class="card-kicker">◎ Design time spent</div>
    <div class="gauge-value">
      <strong>{{ displayValue }}</strong>
      <span>{{ valueLabel }}</span>
    </div>

    <div class="gauge-arc" aria-hidden="true">
      <i class="arc arc-base"></i>
      <i class="arc arc-color"></i>
      <span class="gauge-dot dot-main"></span>
      <span class="gauge-dot dot-left"></span>
      <span class="gauge-dot dot-right"></span>
    </div>

    <div class="gauge-footer">
      <span>{{ leftLabel }}</span>
      <small>{{ centerLabel }}</small>
      <span>{{ rightLabel }}</span>
    </div>
  </article>
</template>

<script setup>
defineProps({
  displayValue: {
    type: [String, Number],
    required: true,
  },
  valueLabel: {
    type: String,
    default: "Index",
  },
  leftLabel: {
    type: String,
    default: "2020",
  },
  centerLabel: {
    type: String,
    default: "Global dataset",
  },
  rightLabel: {
    type: String,
    default: "2026",
  },
});
</script>

<style scoped>
.gauge-card {
  position: relative;
  display: grid;
  align-content: space-between;
  min-height: 428px;
  padding: 16px 18px;
  overflow: hidden;
}

.card-kicker {
  position: relative;
  z-index: 2;
  color: rgba(255, 255, 255, 0.66);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.gauge-value {
  position: relative;
  z-index: 2;
  display: grid;
  justify-items: center;
  margin-top: 54px;
}

.gauge-value strong {
  color: rgba(255, 255, 255, 0.86);
  font-family: var(--font-display);
  font-size: clamp(56px, 6vw, 74px);
  font-weight: 300;
  line-height: 0.9;
}

.gauge-value span,
.gauge-footer small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 14px;
  font-weight: 800;
}

.gauge-arc {
  position: absolute;
  right: -38px;
  bottom: 42px;
  left: -38px;
  height: 220px;
}

.arc {
  position: absolute;
  right: 0;
  bottom: -120px;
  left: 0;
  height: 320px;
  border: 2px solid rgba(255, 255, 255, 0.82);
  border-bottom: 0;
  border-radius: 320px 320px 0 0;
}

.arc-base {
  border-color: rgba(255, 255, 255, 0.24);
}

.arc-color {
  border-color: transparent;
  background:
    conic-gradient(from 248deg at 50% 100%, #f958de 0deg, #15d799 58deg, transparent 59deg);
  clip-path: inset(0 0 48% 0);
  opacity: 0.95;
  filter: saturate(1.2);
}

.arc-color::after {
  position: absolute;
  inset: 24px;
  border-radius: inherit;
  background: #171717;
  content: "";
}

.gauge-dot {
  position: absolute;
  z-index: 3;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 18px rgba(255, 255, 255, 0.86);
}

.dot-main {
  left: 49%;
  top: 64px;
}

.dot-left {
  left: 14%;
  bottom: 78px;
  width: 7px;
  height: 7px;
}

.dot-right {
  right: 14%;
  bottom: 78px;
  width: 7px;
  height: 7px;
}

.gauge-footer {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 76px 1fr 76px;
  align-items: end;
  gap: 12px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 19px;
  font-weight: 900;
}

.gauge-footer small {
  justify-self: center;
  text-align: center;
}

@media (max-width: 760px) {
  .gauge-card {
    min-height: 360px;
  }
}
</style>
