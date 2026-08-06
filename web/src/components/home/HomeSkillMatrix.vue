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
  display: grid;
  min-height: 428px;
  padding: 18px 20px 16px;
  align-content: space-between;
}

.skill-head,
.skill-grid,
.matrix-note {
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
}

.skill-grid li {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 16px;
  line-height: 1.15;
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

@media (max-width: 760px) {
  .skill-card,
  .skill-head,
  .skill-grid {
    display: grid;
  }

  .tool-list {
    display: none;
  }
}
</style>
