const params = new URLSearchParams(location.search);
const title = document.getElementById('title');
const message = document.getElementById('message');
const url = document.getElementById('url');
const copy = document.getElementById('copy');

if (params.has('code')) {
  title.textContent = 'Almost done';
  message.textContent = 'Copy this address and paste it into the terminal to finish connecting your account. The code expires in a few minutes.';
  url.textContent = location.href;
  url.hidden = false;
  copy.hidden = false;
  copy.addEventListener('click', async () => {
    await navigator.clipboard.writeText(location.href);
    copy.textContent = 'Copied';
  });
} else if (params.has('error')) {
  title.textContent = 'Account not connected';
  message.textContent = params.get('error_description') || params.get('error');
}
