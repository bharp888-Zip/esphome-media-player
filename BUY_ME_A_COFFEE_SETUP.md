# Buy Me a Coffee setup

Use this when adding the same Buy Me a Coffee control to similar projects.

## Exact button details

- Link URL: `https://www.buymeacoffee.com/jtenniswood`
- Image URL: `https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png`
- Image alt text: `Buy Me A Coffee`
- Image height: `60`
- Rounded style: `border-radius:999px;`
- Floating web button position: `right:28px;bottom:28px;`

## Docs page button

Add this support block where the docs homepage or README should show the button:

```markdown
## Support This Project

If you find this project useful, consider buying me a coffee to support ongoing development!

<a href="https://www.buymeacoffee.com/jtenniswood" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60" style="border-radius:999px;" />
</a>
```

For README files, omit `target="_blank"` if the project style does not already use it:

```html
<a href="https://www.buymeacoffee.com/jtenniswood">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60" style="border-radius:999px;" />
</a>
```

## VitePress docs floating button

If the project uses VitePress, add a theme component instead of the third-party widget script so the docs match the webserver button style.

Create `docs/.vitepress/theme/components/SupportButton.vue`:

```vue
<template>
  <a
    class="sp-support-btn"
    href="https://www.buymeacoffee.com/jtenniswood"
    target="_blank"
    rel="noopener"
  >
    <img
      src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
      alt="Buy Me A Coffee"
      height="60"
    >
  </a>
</template>
```

Add the support button to the VitePress layout and import the CSS:

```js
import { defineAsyncComponent, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import SupportButton from './components/SupportButton.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(SupportButton),
    })
  },
  enhanceApp({ app }) {
    app.component('InstallButton', defineAsyncComponent(() => import('./components/InstallButton.vue')))
  },
}
```

Add this CSS:

```css
.sp-support-btn{position:fixed;right:28px;bottom:28px;z-index:150;display:inline-block;line-height:0}
.sp-support-btn img{height:60px;display:block;border-radius:999px}
```

## Webserver floating button

Add a fixed-position support link to the webserver JavaScript:

```js
function addSupportButton() {
  if (document.querySelector(".sp-support-btn")) return;
  var link = document.createElement("a");
  link.className = "sp-support-btn";
  link.href = "https://www.buymeacoffee.com/jtenniswood";
  link.target = "_blank";
  link.rel = "noopener";
  link.innerHTML = '<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60" style="border-radius:999px;">';
  document.body.appendChild(link);
}
```

Call `addSupportButton()` after the webserver app has created its main page container.

Add this CSS:

```css
.sp-support-btn{position:fixed;right:28px;bottom:28px;z-index:150;display:inline-block;line-height:0}
.sp-support-btn img{height:60px;display:block;border-radius:999px}
```

## Checks

For this project, run:

```sh
npm run webserver:build
npm run check:generated
npm run docs:build
node --check docs/webserver/src/app.template.js
node --check docs/public/webserver/app.js
```

Other similar projects may have different build commands, but the important checks are:

- Rebuild any generated webserver bundle.
- Run the generated-file check if the project has one.
- Build the docs site if the docs config changed.
- Run a JavaScript syntax check on edited/generated webserver scripts.
