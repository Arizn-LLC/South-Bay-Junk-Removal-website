function element(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text || '';
  return node;
}
function safeUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ? url.href : '';
  } catch { return ''; }
}
function reviewCard(review) {
  const card = element('article', 'pjr-review');
  const head = element('div', 'pjr-review-head');
  const avatar = element('span', 'pjr-avatar', review.name.charAt(0));
  if (safeUrl(review.photo)) {
    const image = new Image();
    image.alt = '';
    image.loading = 'lazy';
    image.src = safeUrl(review.photo);
    avatar.replaceChildren(image);
  }
  const info = document.createElement('div');
  const date = new Date(review.date).toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'});
  info.append(element('p','pjr-review-name',review.name), element('p','pjr-review-date',date));
  head.append(avatar, info, element('span','pjr-google','G'));
  const stars = element('span','pjr-stars','★★★★★');
  stars.setAttribute('aria-label','5 out of 5 stars');
  stars.style.color = 'var(--paige-color-accent)';
  card.append(head, stars, element('p','',review.text));
  return card;
}
async function refresh() {
  const response = await fetch('/gbp-feed.json', {cache:'no-cache'});
  if (!response.ok) return;
  const feed = await response.json();
  const cards = feed.reviews.map(reviewCard);
  document.querySelector('#reviews .pjr-strip').replaceChildren(...cards);
  if (feed.post) {
    const block = document.querySelector('#latest-post');
    block.querySelector('p').textContent = feed.post.text;
    const link = block.querySelector('a');
    link.href = safeUrl(feed.post.url) || document.querySelector('.pjr-allreviews').href;
    if (safeUrl(feed.post.image)) {
      const image = new Image();
      image.src = safeUrl(feed.post.image);
      image.alt = '';
      image.loading = 'lazy';
      image.style.cssText = 'max-width:100%;max-height:360px;border-radius:12px';
      block.querySelector('p').before(image);
    }
    block.hidden = false;
  }
}
refresh().catch(() => {});
