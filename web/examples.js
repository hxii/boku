// ========== AVATARS — generative art per example ==========

document.querySelectorAll('.card-avatar').forEach(function(canvas) {
  var ctx = canvas.getContext('2d');
  var name = canvas.dataset.example;
  var w = 64, h = 64;

  // Deterministic hash from name
  var hash = 0;
  for (var i = 0; i < name.length; i++) {
    hash = ((hash << 5) - hash) + name.charCodeAt(i);
    hash = hash & 0xfffffff; // Convert to 32-bit int
  }

  function seededRandom(seed) {
    var x = Math.sin(seed * 9301 + 49297) * 49297;
    return x - Math.floor(x);
  }

  // Background
  ctx.fillStyle = 'rgba(8, 7, 6, 0.6)';
  ctx.fillRect(0, 0, w, h);

  // Draw unique shapes
  var numShapes = 3 + (hash % 4);
  for (var i = 0; i < numShapes; i++) {
    var seed = hash + i * 1000;
    var isCircle = seededRandom(seed + 0.5) > 0.5;
    var x = seededRandom(seed + 1) * w;
    var y = seededRandom(seed + 2) * h;
    var size = 8 + seededRandom(seed + 3) * 20;
    var hue = 30 + seededRandom(seed + 4) * 20;
    var alpha = 0.2 + seededRandom(seed + 5) * 0.4;

    ctx.fillStyle = 'hsl(' + hue + ', 60%, 45%, ' + alpha + ')';
    ctx.beginPath();
    if (isCircle) {
      ctx.arc(x, y, size / 2, 0, Math.PI * 2);
    } else {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(Date.now() * 0.0005 + seed);
      ctx.rect(-size / 2, -size / 2, size, size);
      ctx.restore();
    }
    ctx.fill();
  }

  // Blinking cursor
  if (Math.floor(Date.now() / 500) % 2 === 0) {
    ctx.fillStyle = 'rgba(212, 160, 74, 0.6)';
    ctx.fillRect(4, h - 6, 8, 2);
  }

  // First letter
  ctx.fillStyle = 'rgba(212, 160, 74, 0.8)';
  ctx.font = 'bold 18px "JetBrains Mono", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(name.charAt(0).toUpperCase(), w / 2, h / 2);
});


// ========== CARD INTERACTION ==========

document.querySelectorAll('.glass-card').forEach(function(card) {
  var name = card.dataset.name;
  var codeDiv = card.querySelector('.example-code');
  var copyBtn = codeDiv.querySelector('.copy-btn');
  var hint = card.querySelector('.expand-hint');
  var pre = codeDiv.querySelector('pre');

  // Card click — toggle open/closed
  card.addEventListener('click', function(e) {
    // If click is inside the code area, ignore
    if (e.target.closest('.example-code')) return;

    codeDiv.classList.toggle('open');
    card.classList.toggle('open');
    hint.innerHTML = codeDiv.classList.contains('open')
      ? '<span class="arrow">›</span> hide yaml'
      : '<span class="arrow">›</span> show yaml';
  });

  // Copy button
  copyBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();

    var text = pre.textContent;
    navigator.clipboard.writeText(text).then(function() {
      copyBtn.textContent = 'copied!';
      copyBtn.classList.add('copied');
      setTimeout(function() {
        copyBtn.textContent = 'copy';
        copyBtn.classList.remove('copied');
      }, 1500);
    }).catch(function() {
      copyBtn.textContent = 'error';
      setTimeout(function() { copyBtn.textContent = 'copy'; }, 1500);
    });
  });
});


// ========== BACKGROUND CANVAS (same as index.html) ==========

var bgCanvas = document.getElementById('bgCanvas');
var bgCtx = bgCanvas.getContext('2d');
var W, H;

function resize() {
  W = bgCanvas.width = window.innerWidth;
  H = bgCanvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

bgCanvas.style.filter = 'blur(36px) contrast(1.08)';

var palette = [
  { h: 32, s: 55, l: 38 }, { h: 36, s: 60, l: 42 },
  { h: 40, s: 50, l: 35 }, { h: 34, s: 65, l: 45 },
  { h: 38, s: 45, l: 32 }, { h: 30, s: 58, l: 40 }
];

function LiquidBlob(cx, cy, baseR, color) {
  this.cx = cx;
  this.cy = cy;
  this.baseR = baseR;
  this.color = color;
  this.verts = 16;
  this.phases = [];
  this.freqs = [];
  this.amps = [];
  for (var i = 0; i < this.verts; i++) {
    this.phases.push(Math.random() * Math.PI * 2);
    this.freqs.push(0.3 + Math.random() * 0.7);
    this.amps.push(0.1 + Math.random() * 0.35);
  }
  this.vx = (Math.random() - 0.5) * 0.15;
  this.vy = (Math.random() - 0.5) * 0.15;
  this.opBase = 0.05 + Math.random() * 0.15;
  this.opAmp = 0.03 + Math.random() * 0.1;
  this.opFreq = 0.6 + Math.random() * 0.8;
  this.opPhase = Math.random() * Math.PI * 2;
}

LiquidBlob.prototype.update = function(dt) {
  this.cx += this.vx;
  this.cy += this.vy;
  var m = this.baseR * 1.2;
  if (this.cx < -m) this.cx = W + m;
  if (this.cx > W + m) this.cx = -m;
  if (this.cy < -m) this.cy = H + m;
  if (this.cy > H + m) this.cy = -m;
};

LiquidBlob.prototype.draw = function(t) {
  var s = t * 0.001;
  bgCtx.beginPath();
  for (var i = 0; i <= this.verts; i++) {
    var idx = i % this.verts;
    var angle = (idx / this.verts) * Math.PI * 2;
    var morph = Math.sin(s * this.freqs[idx] + this.phases[idx]) * this.baseR * this.amps[idx];
    var r = this.baseR + morph;
    var x = this.cx + Math.cos(angle) * r;
    var y = this.cy + Math.sin(angle) * r;
    if (i === 0) bgCtx.moveTo(x, y); else bgCtx.lineTo(x, y);
  }
  bgCtx.closePath();
  var op = Math.min(0.8, Math.max(0.15, this.opBase + Math.sin(s * this.opFreq + this.opPhase) * this.opAmp));
  bgCtx.fillStyle = 'hsl(' + this.color.h + ', ' + this.color.s + '%, ' + this.color.l + '%, ' + op + ')';
  bgCtx.fill();
};

var blobs = [];
var cols = 5, rows = 3;
for (var row = 0; row < rows; row++) {
  for (var col = 0; col < cols; col++) {
    blobs.push(new LiquidBlob(
      ((col + 0.5) * W) / cols + (Math.random() - 0.5) * 80,
      ((row + 0.5) * H) / rows + (Math.random() - 0.5) * 60,
      120 + Math.random() * 120,
      palette[(row * cols + col) % palette.length]
    ));
  }
}
for (var i = 0; i < 6; i++) {
  blobs.push(new LiquidBlob(Math.random() * W, Math.random() * H, 50 + Math.random() * 70, palette[Math.floor(Math.random() * palette.length)]));
}

var lastTime = 0;
function animate(now) {
  var dt = Math.min(now - lastTime, 50);
  lastTime = now;
  bgCtx.clearRect(0, 0, W, H);
  bgCtx.fillStyle = "rgba(8, 7, 6, 0.4)";
  bgCtx.fillRect(0, 0, W, H);
  for (var b = 0; b < blobs.length; b++) {
    blobs[b].update(dt);
    blobs[b].draw(now);
  }
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);


// ========== ENTRANCE ANIMATION ==========

var observer = new IntersectionObserver(
  function(entries) {
    entries.forEach(function(e, i) {
      if (e.isIntersecting) {
        setTimeout(function() { e.target.classList.add('visible'); }, i * 80);
      }
    });
  },
  { threshold: 0.05, rootMargin: "0px 0px -40px 0px" }
);
document.querySelectorAll('.glass-card').forEach(function(el) { observer.observe(el); });
