from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':1123,'height':1587}, device_scale_factor=2)
    pg.goto('file:///home/claude/mvb/infographic/mv-barima-infographic.html')
    pg.wait_for_timeout(600)
    # measure real content height vs A3
    m = pg.evaluate("""() => {
      const el = document.querySelector('.page');
      const mm = 420 * 96/25.4;
      return {scrollH: el.scrollHeight, clientH: el.clientHeight, a3px: mm,
              bodyH: document.body.scrollHeight, overflow: el.scrollHeight - el.clientHeight};
    }""")
    print("MEASURE:", m)
    pg.pdf(path='MV-Barima-Infographic.pdf', format='A3', print_background=True,
           margin={'top':'0','bottom':'0','left':'0','right':'0'}, prefer_css_page_size=True)
    pg.screenshot(path='preview.png', full_page=True)
    b.close()
