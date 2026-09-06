// api/age.js
// Deploy this on Vercel. Every time this URL is requested (e.g. every time
// your GitHub README image loads), it computes your exact age at that
// instant and returns an SVG badge showing it.

const BIRTH_DATE = "2004-05-04T00:00:00"; // May 4, 2004 (adjust the time if you know your birth time)

function getAgeParts(birthDate, now) {
  let years = now.getFullYear() - birthDate.getFullYear();
  let months = now.getMonth() - birthDate.getMonth();
  let days = now.getDate() - birthDate.getDate();
  let hours = now.getHours() - birthDate.getHours();
  let minutes = now.getMinutes() - birthDate.getMinutes();
  let seconds = now.getSeconds() - birthDate.getSeconds();

  if (seconds < 0) { seconds += 60; minutes--; }
  if (minutes < 0) { minutes += 60; hours--; }
  if (hours < 0) { hours += 24; days--; }
  if (days < 0) {
    const prevMonth = new Date(now.getFullYear(), now.getMonth(), 0);
    days += prevMonth.getDate();
    months--;
  }
  if (months < 0) { months += 12; years--; }

  return { years, months, days, hours, minutes, seconds };
}

module.exports = (req, res) => {
  const birth = new Date(BIRTH_DATE);
  const now = new Date();
  const { years, months, days, hours, minutes, seconds } = getAgeParts(birth, now);

  const label = `${years}y ${months}m ${days}d ${hours}h ${minutes}m ${seconds}s`;

  const width = 340;
  const height = 32;

  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <rect width="${width}" height="${height}" rx="4" fill="#24292E"/>
  <text x="12" y="21" font-family="Verdana, sans-serif" font-size="12" fill="#FFFFFF">
    Age: ${label}
  </text>
</svg>`.trim();

  res.setHeader("Content-Type", "image/svg+xml");
  // Short max-age instead of strict no-store — GitHub's image proxy (camo)
  // handles this more reliably, and the badge still updates every ~5s.
  res.setHeader("Cache-Control", "public, max-age=5, s-maxage=5");
  res.status(200).send(svg);
};
