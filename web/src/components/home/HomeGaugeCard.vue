<template>
  <article class="portfolio-card gauge-card">
    <div class="card-kicker">◎ Design time spent</div>
    <div class="gauge-value">
      <strong>{{ displayValue }}</strong>
      <span>{{ valueLabel }}</span>
    </div>

    <div class="gauge-arc" aria-hidden="true">
      <span class="gauge-halo"></span>
      <i class="arc arc-base"></i>
      <i class="arc arc-color"></i>
      <i class="arc arc-sweep"></i>
      <span class="gauge-tick tick-a"></span>
      <span class="gauge-tick tick-b"></span>
      <span class="gauge-tick tick-c"></span>
      <span class="gauge-tick tick-d"></span>
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
  background:
    radial-gradient(circle at 50% 48%, rgba(199, 255, 100, 0.08), transparent 28%),
    radial-gradient(circle at 72% 58%, rgba(21, 215, 153, 0.1), transparent 18%),
    #171717;
}

.gauge-card::before {
  position: absolute;
  inset: 58px 18px 70px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 999px 999px 18px 18px;
  opacity: 0.9;
  content: "";
}

.gauge-card::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0 36%, rgba(255, 255, 255, 0.08) 44%, transparent 52%);
  animation: gaugePanelScan 6.8s ease-in-out infinite;
  content: "";
  pointer-events: none;
}

.card-kicker {
  position: relative;
  z-index: 2;
  color: rgba(255, 255, 255, 0.66);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.gauge-value {
  position: relative;
  z-index: 2;
  display: grid;
  justify-items: center;
  margin-top: 38px;
}

.gauge-value strong {
  color: rgba(255, 255, 255, 0.92);
  font-family: var(--font-display);
  font-size: clamp(56px, 6vw, 74px);
  font-weight: 300;
  line-height: 0.9;
  text-shadow:
    0 0 28px rgba(255, 255, 255, 0.16),
    0 0 54px rgba(199, 255, 100, 0.1);
  animation: gaugeValuePulse 4.2s ease-in-out infinite;
}

.gauge-value span,
.gauge-footer small {
  color: rgba(255, 255, 255, 0.52);
  font-size: 14px;
  font-weight: 800;
}

.gauge-arc {
  position: absolute;
  right: -54px;
  bottom: 40px;
  left: -54px;
  height: 230px;
}

.gauge-halo {
  position: absolute;
  right: 17%;
  bottom: -18px;
  left: 17%;
  height: 120px;
  border-radius: 999px 999px 0 0;
  background: radial-gradient(ellipse at 50% 100%, rgba(199, 255, 100, 0.16), transparent 70%);
  filter: blur(2px);
  animation: gaugeHalo 3.8s ease-in-out infinite;
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
  animation: gaugeArcGlow 3.8s ease-in-out infinite;
}

.arc-color::after {
  position: absolute;
  inset: 24px;
  border-radius: inherit;
  background: #171717;
  content: "";
}

.arc-sweep {
  border-color: transparent;
  background:
    conic-gradient(from 236deg at 50% 100%, transparent 0deg, transparent 28deg, rgba(199, 255, 100, 0.92) 34deg, transparent 42deg, transparent 82deg);
  clip-path: inset(0 0 48% 0);
  opacity: 0.82;
  animation: gaugeSweep 4.8s linear infinite;
}

.arc-sweep::after {
  position: absolute;
  inset: 26px;
  border-radius: inherit;
  background: #171717;
  content: "";
}

.gauge-tick {
  position: absolute;
  z-index: 2;
  width: 26px;
  height: 2px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.42);
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.16);
}

.tick-a {
  left: 18%;
  bottom: 100px;
  transform: rotate(26deg);
}

.tick-b {
  left: 35%;
  top: 54px;
  transform: rotate(62deg);
}

.tick-c {
  right: 35%;
  top: 54px;
  transform: rotate(-62deg);
}

.tick-d {
  right: 18%;
  bottom: 100px;
  transform: rotate(-26deg);
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
  animation: gaugeMainDot 2.8s ease-in-out infinite;
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

@keyframes gaugePanelScan {
  0% {
    transform: translateX(-65%);
    opacity: 0;
  }
  45%,
  55% {
    opacity: 0.65;
  }
  100% {
    transform: translateX(65%);
    opacity: 0;
  }
}

@keyframes gaugeValuePulse {
  0%,
  100% {
    opacity: 0.86;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

@keyframes gaugeHalo {
  0%,
  100% {
    opacity: 0.45;
    transform: scaleX(0.92);
  }
  50% {
    opacity: 0.9;
    transform: scaleX(1.04);
  }
}

@keyframes gaugeArcGlow {
  0%,
  100% {
    filter: saturate(1.15) brightness(0.95);
  }
  50% {
    filter: saturate(1.45) brightness(1.2);
  }
}

@keyframes gaugeSweep {
  to {
    transform: rotate(360deg);
  }
}

@keyframes gaugeMainDot {
  0%,
  100% {
    box-shadow: 0 0 18px rgba(255, 255, 255, 0.86);
    transform: scale(1);
  }
  50% {
    box-shadow:
      0 0 18px rgba(255, 255, 255, 0.95),
      0 0 36px rgba(199, 255, 100, 0.54);
    transform: scale(1.22);
  }
}

@media (max-width: 760px) {
  .gauge-card {
    min-height: 360px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gauge-card::after,
  .gauge-value strong,
  .gauge-halo,
  .arc-color,
  .arc-sweep,
  .dot-main {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
