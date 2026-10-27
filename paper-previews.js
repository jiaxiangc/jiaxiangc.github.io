// Covers stay still until hovered; leaving always restores the selected poster.
(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const previews = Array.from(document.querySelectorAll('.paper-preview'), element => {
    const video = element.querySelector('video');
    const button = element.querySelector('button');
    const cover = document.createElement('img');
    cover.className = 'preview-cover';
    cover.src = video.poster;
    cover.alt = '';
    cover.setAttribute('aria-hidden', 'true');
    cover.width = video.width;
    cover.height = video.height;
    element.insertBefore(cover, button);

    const state = { element, video, visible: true, hovered: false, manualPlay: false, pausedByUser: false };
    const shouldPlay = () => state.visible && !document.hidden && !state.pausedByUser
      && (state.manualPlay || (state.hovered && !reducedMotion.matches));
    const updateButton = () => {
      const paused = video.paused;
      button.dataset.state = paused ? 'paused' : 'playing';
      button.setAttribute('aria-label', `${paused ? 'Play' : 'Pause'} ${element.dataset.paper} preview`);
    };
    const showCover = () => {
      element.classList.remove('is-playing');
      updateButton();
    };
    let playRequest = 0;
    state.sync = () => {
      const request = ++playRequest;
      if (shouldPlay()) {
        video.play().then(() => {
          // Pointer leave can happen before a slow video finishes loading.
          if (request !== playRequest) return;
          if (shouldPlay()) element.classList.add('is-playing');
          else video.pause();
          updateButton();
        }).catch(() => { if (request === playRequest) showCover(); });
      } else {
        video.pause();
        showCover();
        if (video.readyState > 0 && video.currentTime !== 0) video.currentTime = 0;
      }
    };
    state.reset = () => {
      state.hovered = false;
      state.manualPlay = false;
      state.pausedByUser = false;
      state.sync();
    };

    element.addEventListener('pointerenter', event => {
      if (event.pointerType === 'touch') return;
      state.hovered = true;
      state.pausedByUser = false;
      state.sync();
    });
    element.addEventListener('pointerleave', event => {
      if (event.pointerType !== 'touch') state.reset();
    });
    // A mouse click must not cancel playback just started by pointerenter.
    // Touch and keyboard activation still toggle playback explicitly.
    button.addEventListener('click', event => {
      if (event.detail > 0 && state.hovered && !reducedMotion.matches) {
        state.pausedByUser = false;
        state.sync();
        return;
      }
      const playing = shouldPlay();
      state.pausedByUser = playing;
      state.manualPlay = !playing;
      state.sync();
    });
    button.addEventListener('blur', () => {
      if (!state.hovered) state.reset();
    });
    button.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      state.manualPlay = false;
      state.pausedByUser = true;
      state.sync();
    });
    video.addEventListener('pause', () => {
      // Ignore a queued pause event if a newer request has resumed playback.
      if (video.paused) showCover();
    });
    video.addEventListener('playing', () => {
      if (shouldPlay()) element.classList.add('is-playing');
      else video.pause();
      updateButton();
    });
    video.controls = false;
    button.hidden = false;
    element.classList.add('is-enhanced');
    updateButton();
    return state;
  });

  if ('IntersectionObserver' in window) {
    const byElement = new Map(previews.map(state => [state.element, state]));
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const state = byElement.get(entry.target);
        state.visible = entry.isIntersecting;
        if (state.visible) state.sync();
        else state.reset();
      });
    });
    previews.forEach(state => observer.observe(state.element));
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) previews.forEach(state => state.reset());
  });
  reducedMotion.addEventListener('change', () => previews.forEach(state => state.reset()));
})();
