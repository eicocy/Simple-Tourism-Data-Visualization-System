<template>
  <article class="portfolio-card skill-card">
    <div class="skill-head">
      <span>▥ Travel signal matrix</span>
      <b>Tool</b>
    </div>

    <div class="skill-grid">
      <div>
        <strong>Signal</strong>
        <ol>
          <li v-for="skill in skills" :key="skill.name">
            <span>{{ skill.name }}</span>
            <em>
              <b :style="{ width: `${Math.min(Number(skill.score) || 0, 100)}%` }"></b>
            </em>
            <i>{{ skill.score }}</i>
          </li>
        </ol>
      </div>
      <div class="tool-list">
        <strong>Source</strong>
        <span v-for="tool in tools" :key="tool">{{ tool }}</span>
      </div>
    </div>

    <div class="matrix-note">
      <span>// score is normalized</span>
      <b>{{ note }}</b>
    </div>

    <div class="matrix-bars" aria-hidden="true">
      <i
        v-for="bar in bars"
        :key="bar"
        :style="{ '--delay': `${bar * 18}ms` }"
      ></i>
    </div>

    <span class="matrix-scan" aria-hidden="true"></span>
  </article>
</template>

<script setup>
defineProps({
  skills: {
    type: Array,
    required: true,
  },
  tools: {
    type: Array,
    required: true,
  },
  note: {
    type: String,
    default: "always iterating",
  },
});

const bars = Array.from({ length: 118 }, (_, index) => index);
</script>

<style scoped>
.skill-card {
  position: relative;
  display: grid;
  min-height: 428px;
  padding: 18px 20px 16px;
  align-content: space-between;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(255, 255, 255, 0.026) 1px, transparent 1px),
    radial-gradient(circle at 82% 20%, rgba(199, 255, 100, 0.08), transparent 28%),
    #171717;
  background-size: 34px 34px, 34px 34px, auto, auto;
}

.skill-card::before {
  position: absolute;
  inset: 52px 18px 74px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 8px;
  content: "";
  pointer-events: none;
}

.skill-card::after {
  position: absolute;
  top: 70px;
  right: 20px;
  width: 118px;
  height: 118px;
  border: 1px solid rgba(199, 255, 100, 0.16);
  border-radius: 50%;
  background:
    linear-gradient(90deg, transparent 49%, rgba(199, 255, 100, 0.18) 50%, transparent 51%),
    linear-gradient(180deg, transparent 49%, rgba(199, 255, 100, 0.18) 50%, transparent 51%);
  opacity: 0.48;
  animation: matrixRadar 7s linear infinite;
  content: "";
  pointer-events: none;
}

.skill-head,
.skill-grid,
.matrix-note {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.skill-head,
.skill-grid strong,
.matrix-note {
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.skill-grid {
  align-items: start;
}

.skill-grid ol {
  display: grid;
  margin-top: 8px;
  gap: 5px;
}

.skill-grid li {
  display: grid;
  grid-template-columns: minmax(130px, 190px) minmax(62px, 1fr) 30px;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 14px;
  line-height: 1.15;
}

.skill-grid li em {
  position: relative;
  display: block;
  height: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.11);
}

.skill-grid li em::after {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.28), transparent);
  animation: signalTrackSweep 2.8s ease-in-out infinite;
  content: "";
}

.skill-grid li em b {
  position: absolute;
  inset: 0 auto 0 0;
  min-width: 6px;
  border-radius: inherit;
  background: linear-gradient(90deg, #57d5b0, #c7ff64);
  box-shadow: 0 0 16px rgba(199, 255, 100, 0.34);
}

.skill-grid li i {
  min-width: 24px;
  height: 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.72);
  font-size: 10px;
  font-style: normal;
  line-height: 14px;
  text-align: center;
}

.tool-list {
  display: grid;
  justify-items: end;
  color: rgba(255, 255, 255, 0.45);
  font-size: 15px;
  line-height: 1.25;
  text-align: right;
}

.matrix-note {
  align-items: end;
  justify-content: flex-end;
  color: rgba(255, 255, 255, 0.44);
  font-family: var(--font-mono);
  text-transform: none;
}

.matrix-note b {
  color: #c7ff64;
}

.matrix-bars {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(118, 1fr);
  gap: 2px;
  height: 38px;
  align-items: end;
}

.matrix-bars i {
  display: block;
  height: calc(16px + (var(--delay) / 35));
  max-height: 38px;
  border-left: 1px solid rgba(255, 255, 255, 0.22);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), currentColor);
  color: #c7ff64;
  transform-origin: bottom;
  animation: matrixBarPulse 2.6s ease-in-out infinite;
  animation-delay: var(--delay);
}

.matrix-bars i:nth-child(5n + 1) {
  color: #10d89f;
}

.matrix-bars i:nth-child(7n + 2) {
  color: #f958de;
}

.matrix-bars i:nth-child(9n + 3) {
  color: #ff765f;
}

.matrix-bars i:nth-child(11n + 4) {
  color: #ffb84d;
}

.matrix-scan {
  position: absolute;
  top: 54px;
  bottom: 74px;
  left: 20px;
  z-index: 1;
  width: 88px;
  background: linear-gradient(90deg, transparent, rgba(199, 255, 100, 0.1), transparent);
  opacity: 0.8;
  animation: matrixScan 5.2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes signalTrackSweep {
  0%,
  100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
}

@keyframes matrixBarPulse {
  0%,
  100% {
    opacity: 0.46;
    transform: scaleY(0.72);
  }
  50% {
    opacity: 0.94;
    transform: scaleY(1);
  }
}

@keyframes matrixScan {
  0% {
    transform: translateX(-90px);
    opacity: 0;
  }
  45%,
  55% {
    opacity: 0.72;
  }
  100% {
    transform: translateX(calc(100vw + 90px));
    opacity: 0;
  }
}

@keyframes matrixRadar {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .skill-card,
  .skill-head,
  .skill-grid {
    display: grid;
  }

  .tool-list {
    display: none;
  }

  .skill-grid li {
    grid-template-columns: minmax(126px, 1fr) minmax(56px, 0.8fr) 30px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .skill-card::after,
  .skill-grid li em::after,
  .matrix-bars i,
  .matrix-scan {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
  }
}
</style>
