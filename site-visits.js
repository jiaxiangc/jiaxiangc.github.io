// Count only the published homepage, never localhost, file previews, or forks.
(() => {
  const container = document.getElementById('busuanzi_container_site_pv');
  const value = document.getElementById('busuanzi_value_site_pv');
  if (!container || !value) return;

  const setState = (state, title) => {
    container.dataset.state = state;
    container.title = title;
  };

  if (window.location.protocol !== 'https:'
      || window.location.hostname !== 'jiaxiangc.github.io') {
    // Show the footer layout in previews without submitting any views.
    setState('preview', 'Preview only — visits are not counted here.');
    return;
  }

  setState('loading', 'Loading total page views.');
  const unavailable = () => setState('unavailable', 'Page-view count is temporarily unavailable.');

  // Use the same endpoint and referrer policy as Busuanzi's official client.
  // Send only one request: retries can count the same page load more than once.
  const callbackName = 'BusuanziCallback_' + Math.floor(Math.random() * 1099511627776);
  const script = document.createElement('script');
  let settled = false;
  // A timeout changes only the status; a late response can still show the count.
  const timeout = window.setTimeout(unavailable, 8000);
  const finish = (data) => {
    if (settled) return;
    settled = true;
    window.clearTimeout(timeout);
    if (Number.isSafeInteger(data?.site_pv) && data.site_pv >= 0) {
      value.textContent = data.site_pv.toLocaleString('en-US');
      setState('ready', 'Total page views recorded by the counter.');
    } else {
      unavailable();
    }
    script.remove();
    delete window[callbackName];
  };
  window[callbackName] = finish;
  script.src = 'https://busuanzi.ibruce.info/busuanzi?jsonpCallback=' + callbackName;
  script.async = true;
  script.referrerPolicy = 'no-referrer-when-downgrade';
  script.onerror = () => finish();
  script.onload = () => finish(); // Also handle a response that omits the callback.
  document.head.appendChild(script);
})();
