// Count only the published homepage, never localhost, file previews, or forks.
(() => {
  if (window.location.protocol !== 'https:'
      || window.location.hostname !== 'jiaxiangc.github.io') {
    // Show the footer layout in previews without submitting any views.
    document.getElementById('busuanzi_value_site_pv').textContent = '—';
    document.getElementById('busuanzi_container_site_pv').style.display = 'inline';
    document.querySelector('.site-visits').title = 'Preview only — visits are not counted here.';
    return;
  }

  // Display the provider's existing total without resetting it or adding offsets.
  // The counter stays hidden if the service is unavailable or blocked.
  const script = document.createElement('script');
  script.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
  script.async = true;
  document.head.appendChild(script);
})();
