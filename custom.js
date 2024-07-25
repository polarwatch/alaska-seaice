<script>
// custom.js
document.addEventListener("DOMContentLoaded", function() {
  // List of URLs with target=_blank
  const urlsToOpenInNewTab = [
    "https://github.com/polarwatch/alaska-seaice",
    "https://shinyfin.psmfc.org/ak-sst-mhw/",
    "https://polarwatch.noaa.gov"
  ];

  urlsToOpenInNewTab.forEach(url => {
    const link = document.querySelector(`a[href="${url}"]`);
    if (link) {
      link.setAttribute('target', '_blank');
    }
  });
});
</script>

