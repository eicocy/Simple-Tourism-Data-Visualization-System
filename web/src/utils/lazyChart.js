import { nextTick, unref } from "vue";

export function runWhenVisible(target, callback, options = {}) {
  let observer = null;
  let stopped = false;

  const stop = () => {
    stopped = true;
    observer?.disconnect();
    observer = null;
  };

  nextTick(() => {
    if (stopped) {
      return;
    }

    const element = unref(target);
    const run = () => {
      if (stopped) {
        return;
      }
      stop();
      callback();
    };

    if (!element || typeof window === "undefined" || !("IntersectionObserver" in window)) {
      run();
      return;
    }

    observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting || entry.intersectionRatio > 0)) {
          run();
        }
      },
      {
        rootMargin: options.rootMargin || "160px 0px",
        threshold: options.threshold ?? 0.01,
      },
    );

    observer.observe(element);
  });

  return stop;
}
