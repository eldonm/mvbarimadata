/* MV Barima research site — theme toggle, chart hover layer, source browser */
(function () {
  'use strict';

  /* ---------------- theme ---------------- */
  var KEY = 'mvb-theme';
  try {
    var saved = localStorage.getItem(KEY);
    if (saved) document.documentElement.setAttribute('data-theme', saved);
  } catch (e) {}

  /* Light is the default. Dark is opt-in only, and the OS preference is not
     consulted, so every visitor sees the same thing on a first visit. */
  function initTheme() {
    var btn = document.querySelector('.themebtn');
    if (!btn) return;
    function isDark() {
      return document.documentElement.getAttribute('data-theme') === 'dark';
    }
    function label() {
      btn.textContent = isDark() ? 'Light' : 'Dark';
      btn.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme');
    }
    btn.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
      label();
    });
    label();
  }

  /* ---------------- tooltip helper ---------------- */
  function makeTip(host) {
    var tip = document.createElement('div');
    tip.className = 'tip';
    tip.setAttribute('role', 'status');
    host.appendChild(tip);
    return {
      el: tip,
      show: function (x, y, title, rows) {
        while (tip.firstChild) tip.removeChild(tip.firstChild);
        var t = document.createElement('div');
        t.className = 'tt';
        t.textContent = title;
        tip.appendChild(t);
        rows.forEach(function (r) {
          var row = document.createElement('div');
          row.className = 'trow';
          if (r.color) {
            var k = document.createElement('span');
            k.className = 'tk';
            k.style.background = r.color;
            row.appendChild(k);
          }
          var v = document.createElement('span');
          v.className = 'tv';
          v.textContent = r.value;
          row.appendChild(v);
          var n = document.createElement('span');
          n.className = 'tn';
          n.textContent = r.name;
          row.appendChild(n);
          tip.appendChild(row);
        });
        var pad = 8;
        var maxX = host.clientWidth - pad;
        tip.style.left = Math.max(pad + 60, Math.min(x, maxX - 60)) + 'px';
        tip.style.top = (y - 12) + 'px';
        tip.style.opacity = '1';
      },
      hide: function () { tip.style.opacity = '0'; }
    };
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  /* ---------------- line chart (crosshair, snaps to nearest X) ---------------- */
  function initLineChart(root) {
    var svg = root.querySelector('svg');
    if (!svg) return;
    var data;
    try { data = JSON.parse(root.getAttribute('data-series')); } catch (e) { return; }
    var tip = makeTip(root);
    var cross = svg.querySelector('.crosshair');
    var hits = svg.querySelectorAll('.hit');

    Array.prototype.forEach.call(hits, function (h) {
      var i = parseInt(h.getAttribute('data-i'), 10);
      function on() {
        var r = h.getBoundingClientRect();
        var hr = root.getBoundingClientRect();
        var cx = r.left - hr.left + r.width / 2;
        if (cross) {
          cross.setAttribute('x1', h.getAttribute('data-x'));
          cross.setAttribute('x2', h.getAttribute('data-x'));
          cross.style.opacity = '1';
        }
        var rows = data.series.map(function (s) {
          return { color: cssVar(s.varname) || s.fallback, value: String(s.values[i]), name: s.name };
        });
        tip.show(cx, r.top - hr.top + 26, data.labels[i], rows);
      }
      function off() {
        tip.hide();
        if (cross) cross.style.opacity = '0';
      }
      h.addEventListener('pointerenter', on);
      h.addEventListener('pointermove', on);
      h.addEventListener('pointerleave', off);
      h.addEventListener('focus', on);
      h.addEventListener('blur', off);
      h.setAttribute('tabindex', '0');
      h.setAttribute('role', 'img');
      h.setAttribute('aria-label',
        data.labels[i] + ': ' + data.series.map(function (s) { return s.values[i] + ' ' + s.name; }).join(', '));
    });
  }

  /* ---------------- bar charts (mark is the hit target) ---------------- */
  function initBarChart(root) {
    var svg = root.querySelector('svg');
    if (!svg) return;
    var tip = makeTip(root);
    var marks = svg.querySelectorAll('[data-value]');
    Array.prototype.forEach.call(marks, function (m) {
      function on() {
        var r = m.getBoundingClientRect();
        var hr = root.getBoundingClientRect();
        Array.prototype.forEach.call(marks, function (o) { if (o !== m) o.classList.add('dim'); });
        var rows = [{
          color: cssVar(m.getAttribute('data-var')) || '',
          value: m.getAttribute('data-value'),
          name: m.getAttribute('data-unit') || ''
        }];
        var extra = m.getAttribute('data-note');
        if (extra) rows.push({ color: '', value: '', name: extra });
        tip.show(r.left - hr.left + r.width / 2, r.top - hr.top + 4, m.getAttribute('data-label'), rows);
      }
      function off() {
        tip.hide();
        Array.prototype.forEach.call(marks, function (o) { o.classList.remove('dim'); });
      }
      m.addEventListener('pointerenter', on);
      m.addEventListener('pointerleave', off);
      m.addEventListener('focus', on);
      m.addEventListener('blur', off);
      m.setAttribute('tabindex', '0');
      m.setAttribute('role', 'img');
      m.setAttribute('aria-label', m.getAttribute('data-label') + ': ' +
        m.getAttribute('data-value') + ' ' + (m.getAttribute('data-unit') || ''));
    });
  }

  /* ---------------- source browser ---------------- */
  function initBrowser() {
    var list = document.getElementById('srclist');
    if (!list) return;
    var q = document.getElementById('f-q');
    var outlet = document.getElementById('f-outlet');
    var kind = document.getElementById('f-kind');
    var period = document.getElementById('f-period');
    var sort = document.getElementById('f-sort');
    var count = document.getElementById('f-count');
    var clear = document.getElementById('f-clear');
    var items = Array.prototype.slice.call(list.querySelectorAll('.src'));

    var cache = items.map(function (el) {
      return {
        el: el,
        hay: (el.getAttribute('data-search') || '').toLowerCase(),
        outlet: el.getAttribute('data-outlet') || '',
        kind: el.getAttribute('data-kind') || '',
        date: el.getAttribute('data-date') || '',
        title: (el.querySelector('h3') ? el.querySelector('h3').textContent : '').toLowerCase()
      };
    });

    /* Map each published date to its datebar (built into the static HTML). */
    var datebars = {};
    Array.prototype.forEach.call(list.querySelectorAll('.datebar'), function (bar) {
      var s = bar.nextElementSibling;
      while (s && !s.classList.contains('src') && !s.classList.contains('datebar')) {
        s = s.nextElementSibling;
      }
      if (s && s.classList.contains('src')) {
        datebars[s.getAttribute('data-date') || ''] = bar;
      }
    });

    function setBarVisible(bar, on) {
      bar.hidden = !on;
      bar.classList.toggle('is-filtered-out', !on);
      bar.style.display = on ? '' : 'none';
    }

    function inPeriod(d, p) {
      if (!p) return true;
      if (p === 'pre') return d < '2026-07-18';
      if (p === 'disaster') return d >= '2026-07-18' && d <= '2026-07-21';
      if (p === 'reckoning') return d >= '2026-07-22';
      return true;
    }

    function apply() {
      var terms = (q.value || '').toLowerCase().split(/\s+/).filter(Boolean);
      var n = 0;
      cache.forEach(function (c) {
        var ok = terms.every(function (t) { return c.hay.indexOf(t) !== -1; }) &&
                 (!outlet.value || c.outlet === outlet.value) &&
                 (!kind.value || c.kind === kind.value) &&
                 inPeriod(c.date, period.value);
        c.el.hidden = !ok;
        c.el.classList.toggle('is-filtered-out', !ok);
        c.el.style.display = ok ? '' : 'none';
        if (ok) n++;
      });
      count.textContent = n + (n === 1 ? ' document' : ' documents') + ' shown of ' + cache.length;
      Array.prototype.forEach.call(document.querySelectorAll('.datebar'), function (b) {
        if (b.getAttribute('data-grouped') === '0') {
          setBarVisible(b, false);
          return;
        }
        var any = false, s = b.nextElementSibling;
        while (s && !s.classList.contains('datebar')) {
          if (s.classList.contains('src') && !s.hidden) { any = true; break; }
          s = s.nextElementSibling;
        }
        setBarVisible(b, any);
      });
      var empty = document.getElementById('srcempty');
      if (empty) {
        empty.hidden = n !== 0;
        empty.classList.toggle('is-filtered-out', n !== 0);
        empty.style.display = n === 0 ? '' : 'none';
      }
    }

    function resort() {
      var mode = sort.value;
      var sorted = cache.slice().sort(function (a, b) {
        if (mode === 'oldest') return a.date < b.date ? -1 : a.date > b.date ? 1 : 0;
        if (mode === 'outlet') return a.outlet.localeCompare(b.outlet) || (a.date < b.date ? 1 : -1);
        if (mode === 'title') return a.title.localeCompare(b.title);
        return a.date > b.date ? -1 : a.date < b.date ? 1 : 0;
      });
      var groups = mode === 'newest' || mode === 'oldest';
      var d, bar, last = null;

      if (groups) {
        sorted.forEach(function (c) {
          if (c.date !== last) {
            last = c.date;
            bar = datebars[c.date];
            if (bar) {
              bar.setAttribute('data-grouped', '1');
              list.appendChild(bar);
            }
          }
          list.appendChild(c.el);
        });
        for (d in datebars) {
          if (Object.prototype.hasOwnProperty.call(datebars, d)) {
            datebars[d].setAttribute('data-grouped', '1');
          }
        }
      } else {
        for (d in datebars) {
          if (Object.prototype.hasOwnProperty.call(datebars, d)) {
            bar = datebars[d];
            bar.setAttribute('data-grouped', '0');
            setBarVisible(bar, false);
            list.appendChild(bar);
          }
        }
        sorted.forEach(function (c) { list.appendChild(c.el); });
      }
      apply();
    }

    [q, outlet, kind, period].forEach(function (c) {
      c.addEventListener('input', apply);
      c.addEventListener('change', apply);
    });
    sort.addEventListener('change', resort);
    clear.addEventListener('click', function () {
      q.value = ''; outlet.value = ''; kind.value = ''; period.value = ''; sort.value = 'newest';
      resort();
    });

    /* deep link: ?q=... */
    var params = new URLSearchParams(location.search);
    if (params.get('q')) q.value = params.get('q');
    if (params.get('outlet')) outlet.value = params.get('outlet');
    if (params.get('kind')) kind.value = params.get('kind');
    apply();
  }

  /* ---------------- collapsible questions ----------------
     The markup works with this file absent: <details> opens on click by itself.
     This only adds expand-all, deep-linking and print behaviour on top. */
  function initQA() {
    var items = Array.prototype.slice.call(document.querySelectorAll('details.qa'));
    if (!items.length) return;

    var controls = document.querySelector('.qacontrols');
    if (controls) {
      controls.addEventListener('click', function (e) {
        var mode = e.target && e.target.getAttribute && e.target.getAttribute('data-qa');
        if (!mode) return;
        items.forEach(function (d) { d.open = mode === 'open'; });
      });
    }

    /* Deep link: /questions.html#q3 opens that question and scrolls to it. */
    function openFromHash() {
      var id = (location.hash || '').replace('#', '');
      if (!id) return;
      var el = document.getElementById(id);
      if (el && el.tagName === 'DETAILS') {
        el.open = true;
        el.scrollIntoView({ block: 'start' });
      }
    }
    openFromHash();
    window.addEventListener('hashchange', openFromHash);

    /* Clicking a question puts its id in the address bar, so a reader can copy
       a link to one answer. replaceState, so the back button is not polluted. */
    items.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (d.open && d.id && history.replaceState) {
          history.replaceState(null, '', '#' + d.id);
        }
      });
    });

    /* Print the whole page, not just what happens to be open. */
    var wasOpen = null;
    window.addEventListener('beforeprint', function () {
      wasOpen = items.map(function (d) { return d.open; });
      items.forEach(function (d) { d.open = true; });
    });
    window.addEventListener('afterprint', function () {
      if (!wasOpen) return;
      items.forEach(function (d, i) { d.open = wasOpen[i]; });
      wasOpen = null;
    });
  }

  /* ---------------- go ---------------- */
  function ready() {
    initTheme();
    Array.prototype.forEach.call(document.querySelectorAll('.chart[data-series]'), initLineChart);
    Array.prototype.forEach.call(document.querySelectorAll('.chart.bars'), initBarChart);
    initBrowser();
    initQA();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();
})();
