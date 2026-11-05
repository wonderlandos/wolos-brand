// SPDX-License-Identifier: BSD-2-Clause
// A small DOM for node, made here (no linkedom, no jsdom, no dependency; DS-WEB-1, ADR 0058).
// It runs the light-DOM custom elements of the web kit (webapps/kit/wolkit.js) without a browser:
// elements and text nodes, attributes with the reflecting properties the kit uses, dataset, a
// selector engine (tag, #id, .class, [attr], [attr=v], :scope, descendant and child combinators,
// comma lists), events that bubble (target, currentTarget, preventDefault, stopPropagation),
// custom element lifecycle (upgrade, connected, disconnected, attributeChanged), focus, <dialog>,
// location with hashchange, keyboard and click helpers with the default actions that matter.
// It is not a browser: no layout, no style cascade, no focus trap, no shadow DOM, no real HTML
// parser (a small one for test markup). What it cannot do, a test must not claim; the browser test
// of an app (webapps/doctor/test/doctor.test.mjs, CHROME) is where layout and focus are checked.
//
//   const dom = createDom();
//   dom.load(readFileSync("webapps/kit/wolkit.js", "utf8"));   // runs in the page's global
//   const list = dom.mount('<wol-list heading="Checks"><wol-row label="Sound"></wol-row></wol-list>');
//   dom.click(dom.document.querySelector("wol-row"));
//   await dom.settle();                                         // microtasks (queueMicrotask, promises)
import vm from "node:vm";

const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]);
const NODE = { ELEMENT: 1, TEXT: 3, DOCUMENT: 9 };
const FOCUSABLE_TAGS = new Set(["input", "textarea", "select", "button"]);
const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " " };
const decode = (s) => s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
  if (e[0] === "#") return String.fromCodePoint(e[1].toLowerCase() === "x" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
  return ENTITIES[e.toLowerCase()] ?? m;
});
const escText = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const escAttr = (s) => escText(s).replace(/"/g, "&quot;");
const camel = (k) => k.replace(/-([a-z])/g, (m, c) => c.toUpperCase());
const dash = (k) => k.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase());

// ---- selectors -------------------------------------------------------------------------------
/** "a > b c, d" -> [[{compound, comb}...]...] (comb = how it relates to the one before it). */
function parseSelector(sel) {
  const out = [];
  for (const part of splitTop(sel)) {
    const chain = [];
    let rest = part.trim();
    let comb = " ";
    if (!rest) throw new Error(`dom-stub: empty selector in "${sel}"`);
    while (rest) {
      const m = /^(?:(\*|[a-zA-Z][\w-]*)|(?=[#.[:]))((?:#[\w-]+|\.[\w-]+|\[[^\]]+\]|:[\w-]+)*)/.exec(rest);
      if (!m || (!m[1] && !m[2])) throw new Error(`dom-stub: unsupported selector "${sel}" at "${rest}"`);
      const c = { tag: m[1] && m[1] !== "*" ? m[1].toLowerCase() : null, id: null, classes: [], attrs: [], scope: false };
      for (const p of m[2].match(/#[\w-]+|\.[\w-]+|\[[^\]]+\]|:[\w-]+/g) || []) {
        if (p[0] === "#") c.id = p.slice(1);
        else if (p[0] === ".") c.classes.push(p.slice(1));
        else if (p === ":scope") c.scope = true;
        else if (p[0] === ":") throw new Error(`dom-stub: unsupported pseudo-class ${p} in "${sel}"`);
        else {
          const a = /^\[\s*([\w:-]+)\s*(?:(=|~=|\^=|\$=|\*=)\s*(?:"([^"]*)"|'([^']*)'|([^\]\s]+))\s*)?\]$/.exec(p);
          if (!a) throw new Error(`dom-stub: unsupported attribute selector ${p} in "${sel}"`);
          c.attrs.push({ name: a[1].toLowerCase(), op: a[2] || null, value: a[3] ?? a[4] ?? a[5] ?? "" });
        }
      }
      chain.push({ c, comb });
      rest = rest.slice(m[0].length);
      const g = /^\s*(>)?\s*/.exec(rest);
      comb = g[1] ? ">" : g[0] ? " " : "";
      rest = rest.slice(g[0].length);
      if (!rest && g[1]) throw new Error(`dom-stub: dangling combinator in "${sel}"`);
    }
    out.push(chain);
  }
  return out;
}
function splitTop(s) {
  const parts = [];
  let depth = 0, cur = "", q = "";
  for (const ch of s) {
    if (q) { if (ch === q) q = ""; } else if (ch === '"' || ch === "'") q = ch;
    else if (ch === "[") depth++; else if (ch === "]") depth--;
    else if (ch === "," && !depth) { parts.push(cur); cur = ""; continue; }
    cur += ch;
  }
  parts.push(cur);
  return parts;
}
function matchCompound(el, c, scope) {
  if (c.tag && el.localName !== c.tag) return false;
  if (c.id && el.getAttribute("id") !== c.id) return false;
  if (c.scope && el !== scope) return false;
  const cls = (el.getAttribute("class") || "").split(/\s+/);
  if (!c.classes.every((k) => cls.includes(k))) return false;
  for (const a of c.attrs) {
    const v = el.getAttribute(a.name);
    if (v === null) return false;
    if (a.op === "=" && v !== a.value) return false;
    if (a.op === "~=" && !v.split(/\s+/).includes(a.value)) return false;
    if (a.op === "^=" && !v.startsWith(a.value)) return false;
    if (a.op === "$=" && !v.endsWith(a.value)) return false;
    if (a.op === "*=" && !v.includes(a.value)) return false;
  }
  return true;
}
function matchChain(el, chain, i, scope) {
  if (!matchCompound(el, chain[i].c, scope)) return false;
  if (i === 0) return true;
  const comb = chain[i].comb;
  if (comb === ">") { const p = el.parentNode; return !!p && p.nodeType === NODE.ELEMENT && matchChain(p, chain, i - 1, scope); }
  for (let p = el.parentNode; p && p.nodeType === NODE.ELEMENT; p = p.parentNode) if (matchChain(p, chain, i - 1, scope)) return true;
  return false;
}
const matchesAny = (el, parsed, scope) => parsed.some((chain) => matchChain(el, chain, chain.length - 1, scope));

/** el.style: property writes land in the style attribute ("width: 40%"), as in a browser. */
function styleOf(el) {
  const props = new Map();
  const sync = () => { if (props.size) el.setAttribute("style", [...props].map(([k, v]) => `${k}: ${v}`).join("; ")); else el.removeAttribute("style"); };
  return new Proxy({}, {
    get: (_, k) => (k === "cssText" ? el.getAttribute("style") ?? "" : props.get(dash(String(k))) ?? ""),
    set: (_, k, v) => { if (v === "" || v == null) props.delete(dash(String(k))); else props.set(dash(String(k)), String(v)); sync(); return true; },
  });
}

// ---- the DOM ---------------------------------------------------------------------------------
export function createDom({ url = "file:///usr/share/wolos/webapps/kit/index.html" } = {}) {
  const registry = new Map(); // name -> { cls, observed }
  const byClass = new Map(); // cls -> name
  const errors = [];

  class Event {
    constructor(type, init = {}) {
      this.type = type;
      this.bubbles = !!init.bubbles;
      this.cancelable = !!init.cancelable;
      this.defaultPrevented = false;
      this.target = null;
      this.currentTarget = null;
      this._stop = false;
    }
    preventDefault() { if (this.cancelable) this.defaultPrevented = true; }
    stopPropagation() { this._stop = true; }
    stopImmediatePropagation() { this._stop = true; this._stopNow = true; }
  }
  class CustomEvent extends Event { constructor(type, init = {}) { super(type, init); this.detail = init.detail ?? null; } }
  class KeyboardEvent extends Event {
    constructor(type, init = {}) {
      super(type, { bubbles: true, cancelable: true, ...init });
      this.key = init.key ?? "";
      this.ctrlKey = !!init.ctrlKey;
      this.metaKey = !!init.metaKey;
      this.altKey = !!init.altKey;
      this.shiftKey = !!init.shiftKey;
    }
  }
  class MouseEvent extends Event { constructor(type, init = {}) { super(type, { bubbles: true, cancelable: true, ...init }); this.button = init.button ?? 0; } }

  /** Listeners and dispatch; `parentOf(target)` gives the next stop of the bubbling path. */
  const targetMixin = {
    addEventListener(type, fn, opts) {
      const once = typeof opts === "object" && !!opts?.once;
      const l = (this._listeners ||= new Map()).get(type) || [];
      if (!l.some((x) => x.fn === fn)) l.push({ fn, once });
      this._listeners.set(type, l);
    },
    removeEventListener(type, fn) {
      const l = this._listeners?.get(type);
      if (l) this._listeners.set(type, l.filter((x) => x.fn !== fn));
    },
    dispatchEvent(ev) {
      ev.target = this;
      for (let n = this; n && !ev._stop; n = n._eventParent()) {
        ev.currentTarget = n;
        for (const l of [...(n._listeners?.get(ev.type) || [])]) {
          if (l.once) n.removeEventListener(ev.type, l.fn);
          try { l.fn.call(n, ev); } catch (e) { errors.push(e); throw e; }
          if (ev._stopNow) break;
        }
        if (!ev.bubbles && n === this) break;
      }
      ev.currentTarget = null;
      return !ev.defaultPrevented;
    },
  };

  class Node {
    constructor() { this.parentNode = null; this.childNodes = []; this._conn = false; }
    _eventParent() { return this.parentNode; }
    get nodeType() { return 0; }
    get parentElement() { const p = this.parentNode; return p && p.nodeType === NODE.ELEMENT ? p : null; }
    get firstChild() { return this.childNodes[0] ?? null; }
    get lastChild() { return this.childNodes[this.childNodes.length - 1] ?? null; }
    get previousSibling() { const p = this.parentNode; return p ? p.childNodes[p.childNodes.indexOf(this) - 1] ?? null : null; }
    get nextSibling() { const p = this.parentNode; return p ? p.childNodes[p.childNodes.indexOf(this) + 1] ?? null : null; }
    get isConnected() { let n = this; while (n.parentNode) n = n.parentNode; return n === document; }
    contains(o) { for (let n = o; n; n = n.parentNode) if (n === this) return true; return false; }
    _inclusive() { return [this, ...this.childNodes.flatMap((c) => c._inclusive())]; }
    _adopt(kids) {
      return kids.flatMap((k) => (typeof k === "string" || typeof k === "number" ? [new Text(String(k))] : k instanceof Node ? [k] : [new Text(String(k))]));
    }
    insertBefore(node, ref) {
      if (node.contains(this)) throw new Error("dom-stub: HierarchyRequestError, a node cannot contain itself");
      if (node.parentNode) node.parentNode.removeChild(node);
      const i = ref ? this.childNodes.indexOf(ref) : this.childNodes.length;
      if (i < 0) throw new Error("dom-stub: NotFoundError, the reference node is not a child");
      this.childNodes.splice(i, 0, node);
      node.parentNode = this;
      const nodes = node._inclusive();
      if (this.isConnected) for (const n of nodes) if (n.nodeType === NODE.ELEMENT) n._connect();
      return node;
    }
    appendChild(node) { return this.insertBefore(node, null); }
    removeChild(node) {
      const i = this.childNodes.indexOf(node);
      if (i < 0) throw new Error("dom-stub: NotFoundError, not a child");
      const was = node._inclusive();
      this.childNodes.splice(i, 1);
      node.parentNode = null;
      for (const n of was) if (n.nodeType === NODE.ELEMENT) n._disconnect();
      if (was.includes(document._active)) document._active = null;
      return node;
    }
    append(...kids) { for (const k of this._adopt(kids)) this.appendChild(k); }
    prepend(...kids) { const first = this.firstChild; for (const k of this._adopt(kids)) this.insertBefore(k, first); }
    replaceChildren(...kids) { for (const c of [...this.childNodes]) this.removeChild(c); this.append(...kids); }
    remove() { if (this.parentNode) this.parentNode.removeChild(this); }
    get textContent() { return this.childNodes.map((c) => c.textContent).join(""); }
    set textContent(v) { this.replaceChildren(...(String(v) === "" ? [] : [String(v)])); }
  }
  Object.assign(Node.prototype, targetMixin);

  class Text extends Node {
    constructor(data = "") { super(); this.data = String(data); }
    get nodeType() { return NODE.TEXT; }
    get nodeName() { return "#text"; }
    get textContent() { return this.data; }
    set textContent(v) { this.data = String(v); }
    _connect() {}
    _disconnect() {}
  }

  class Element extends Node {
    constructor() { super(); this.localName = ""; this._attrs = new Map(); this._ce = null; this.style = styleOf(this); }
    get nodeType() { return NODE.ELEMENT; }
    get tagName() { return this.localName.toUpperCase(); }
    get nodeName() { return this.tagName; }
    // attributes
    getAttribute(k) { k = k.toLowerCase(); return this._attrs.has(k) ? this._attrs.get(k) : null; }
    hasAttribute(k) { return this._attrs.has(k.toLowerCase()); }
    getAttributeNames() { return [...this._attrs.keys()]; }
    setAttribute(k, v) { k = k.toLowerCase(); const old = this.getAttribute(k); this._attrs.set(k, String(v)); this._changed(k, old, String(v)); }
    removeAttribute(k) { k = k.toLowerCase(); if (!this._attrs.has(k)) return; const old = this._attrs.get(k); this._attrs.delete(k); this._changed(k, old, null); }
    toggleAttribute(k, force) {
      const on = force === undefined ? !this.hasAttribute(k) : !!force;
      if (on) { if (!this.hasAttribute(k)) this.setAttribute(k, ""); } else this.removeAttribute(k);
      return on;
    }
    _changed(k, old, now) {
      const ce = this._ce;
      if (ce && ce.observed.includes(k) && this.attributeChangedCallback) this.attributeChangedCallback(k, old, now);
    }
    // custom element lifecycle
    _connect() {
      if (this._conn || !this.isConnected) return;
      this._upgrade();
      this._conn = true;
      if (this._ce && this.connectedCallback) this.connectedCallback();
    }
    _disconnect() {
      if (!this._conn || this.isConnected) return;
      this._conn = false;
      if (this._ce && this.disconnectedCallback) this.disconnectedCallback();
    }
    _upgrade() {
      const def = registry.get(this.localName);
      if (!def || this._ce) return;
      Object.setPrototypeOf(this, def.cls.prototype);
      this._ce = def;
      for (const [k, v] of this._attrs) if (def.observed.includes(k) && this.attributeChangedCallback) this.attributeChangedCallback(k, null, v);
    }
    // tree
    get children() { return this.childNodes.filter((c) => c.nodeType === NODE.ELEMENT); }
    get firstElementChild() { return this.children[0] ?? null; }
    get childElementCount() { return this.children.length; }
    _descendants() { return this.children.flatMap((c) => [c, ...c._descendants()]); }
    querySelectorAll(sel) { const p = parseSelector(sel); return this._descendants().filter((e) => matchesAny(e, p, this)); }
    querySelector(sel) { const p = parseSelector(sel); return this._descendants().find((e) => matchesAny(e, p, this)) ?? null; }
    matches(sel) { return matchesAny(this, parseSelector(sel), this); }
    closest(sel) { const p = parseSelector(sel); for (let n = this; n && n.nodeType === NODE.ELEMENT; n = n.parentNode) if (matchesAny(n, p, n)) return n; return null; }
    // reflecting properties
    get id() { return this.getAttribute("id") ?? ""; }
    set id(v) { this.setAttribute("id", v); }
    get className() { return this.getAttribute("class") ?? ""; }
    set className(v) { this.setAttribute("class", v); }
    get classList() {
      const self = this;
      const get = () => (self.getAttribute("class") || "").split(/\s+/).filter(Boolean);
      return {
        contains: (c) => get().includes(c),
        add: (...c) => self.setAttribute("class", [...new Set([...get(), ...c])].join(" ")),
        remove: (...c) => self.setAttribute("class", get().filter((x) => !c.includes(x)).join(" ")),
        toggle(c, force) { const on = force === undefined ? !get().includes(c) : !!force; if (on) this.add(c); else this.remove(c); return on; },
        get length() { return get().length; },
      };
    }
    get hidden() { return this.hasAttribute("hidden"); }
    set hidden(v) { this.toggleAttribute("hidden", !!v); }
    get title() { return this.getAttribute("title") ?? ""; }
    set title(v) { this.setAttribute("title", v); }
    get slot() { return this.getAttribute("slot") ?? ""; }
    set slot(v) { this.setAttribute("slot", v); }
    get lang() { return this.getAttribute("lang") ?? ""; }
    set lang(v) { this.setAttribute("lang", v); }
    get isContentEditable() { return this.getAttribute("contenteditable") === "" || this.getAttribute("contenteditable") === "true"; }
    get dataset() {
      const self = this;
      const attr = (k) => "data-" + dash(k);
      return new Proxy({}, {
        get: (_, k) => (typeof k === "string" ? self.getAttribute(attr(k)) ?? undefined : undefined),
        set: (_, k, v) => { self.setAttribute(attr(k), v); return true; },
        has: (_, k) => typeof k === "string" && self.hasAttribute(attr(k)),
        deleteProperty: (_, k) => { self.removeAttribute(attr(k)); return true; },
        ownKeys: () => self.getAttributeNames().filter((n) => n.startsWith("data-")).map((n) => camel(n.slice(5))),
        getOwnPropertyDescriptor: (_, k) => (typeof k === "string" && self.hasAttribute(attr(k))
          ? { value: self.getAttribute(attr(k)), enumerable: true, configurable: true, writable: true } : undefined),
      });
    }
    // focus: natively focusable tags and anything with a tabindex, never a disabled control
    get tabIndex() {
      const t = this.getAttribute("tabindex");
      if (t !== null && /^-?\d+$/.test(t)) return Number(t);
      return FOCUSABLE_TAGS.has(this.localName) || (this.localName === "a" && this.hasAttribute("href")) ? 0 : -1;
    }
    set tabIndex(v) { this.setAttribute("tabindex", v); }
    _canFocus() {
      if (!this.isConnected || this.hasAttribute("hidden")) return false;
      if (this.hasAttribute("disabled") && FOCUSABLE_TAGS.has(this.localName)) return false;
      return this.hasAttribute("tabindex") || FOCUSABLE_TAGS.has(this.localName) || (this.localName === "a" && this.hasAttribute("href"));
    }
    focus() {
      if (!this._canFocus() || document.activeElement === this) return;
      const prev = document.activeElement;
      document.activeElement = this;
      if (prev) prev.dispatchEvent(new Event("blur"));
      this.dispatchEvent(new Event("focus"));
    }
    blur() { if (document.activeElement === this) { document.activeElement = null; this.dispatchEvent(new Event("blur")); } }
    click() {
      if (this.hasAttribute("disabled") && FOCUSABLE_TAGS.has(this.localName)) return;
      const ev = new MouseEvent("click");
      const go = this.dispatchEvent(ev);
      if (!go) return;
      const a = this.closest("a[href]");
      if (a) location.href = a.getAttribute("href");
    }
    // markup
    get innerHTML() { return this.childNodes.map(serialize).join(""); }
    set innerHTML(v) { this.replaceChildren(...parseInto(String(v))); }
    get outerHTML() { return serialize(this); }
  }

  class HTMLElement extends Element {
    constructor() {
      super();
      const name = byClass.get(new.target);
      if (!name) throw new TypeError("Illegal constructor (dom-stub: construct a defined custom element, or use document.createElement)");
      this.localName = name;
      this._ce = registry.get(name);
    }
  }
  // HTMLElement's constructor refuses classes that are not defined custom elements, so the
  // built-in tags (made by createElement or the parser, never by `new`) share a private base.
  class Plain extends Element { constructor(name) { super(); this.localName = name; } }
  class HTMLButtonElement extends Plain {
    get type() { return this.getAttribute("type") ?? "submit"; } set type(v) { this.setAttribute("type", v); }
    get disabled() { return this.hasAttribute("disabled"); } set disabled(v) { this.toggleAttribute("disabled", !!v); }
  }
  class HTMLInputElement extends Plain {
    constructor(n) { super(n); this._value = null; }
    get type() { return this.getAttribute("type") ?? "text"; } set type(v) { this.setAttribute("type", v); }
    get value() { return this._value ?? this.getAttribute("value") ?? ""; } set value(v) { this._value = String(v); }
    get placeholder() { return this.getAttribute("placeholder") ?? ""; } set placeholder(v) { this.setAttribute("placeholder", v); }
    get autocomplete() { return this.getAttribute("autocomplete") ?? ""; } set autocomplete(v) { this.setAttribute("autocomplete", v); }
    get spellcheck() { return this.getAttribute("spellcheck") !== "false"; } set spellcheck(v) { this.setAttribute("spellcheck", String(!!v)); }
    get disabled() { return this.hasAttribute("disabled"); } set disabled(v) { this.toggleAttribute("disabled", !!v); }
  }
  class HTMLAnchorElement extends Plain {
    get href() { return this.hasAttribute("href") ? new URL(this.getAttribute("href"), location.href).href : ""; } set href(v) { this.setAttribute("href", v); }
    get hash() { const h = this.hasAttribute("href") ? new URL(this.getAttribute("href"), location.href).hash : ""; return h === "#" ? "" : h; }
  }
  class HTMLDialogElement extends Plain {
    get open() { return this.hasAttribute("open"); } set open(v) { this.toggleAttribute("open", !!v); }
    showModal() { if (this.open) throw new Error("dom-stub: InvalidStateError, the dialog is already open"); this.open = true; this.modal = true; }
    show() { this.open = true; }
    close(result) { if (!this.open) return; this.open = false; this.modal = false; this.returnValue = result ?? ""; this.dispatchEvent(new Event("close")); }
  }
  const BUILTIN = { button: HTMLButtonElement, input: HTMLInputElement, a: HTMLAnchorElement, dialog: HTMLDialogElement };

  function makeElement(name) {
    name = name.toLowerCase();
    const def = registry.get(name);
    if (def) return new def.cls();
    const C = BUILTIN[name] || Plain;
    return new C(name);
  }

  // ---- markup ----
  function serialize(n) {
    if (n.nodeType === NODE.TEXT) return escText(n.data);
    const attrs = [...n._attrs].map(([k, v]) => ` ${k}="${escAttr(v)}"`).join("");
    return VOID.has(n.localName) ? `<${n.localName}${attrs}>` : `<${n.localName}${attrs}>${n.childNodes.map(serialize).join("")}</${n.localName}>`;
  }
  /** Parses markup into detached nodes (plain elements; they upgrade when they are connected). */
  function parseInto(html) {
    const root = new Plain("#fragment");
    const stack = [root];
    const re = /<!--[\s\S]*?-->|<\/([a-zA-Z][\w-]*)\s*>|<([a-zA-Z][\w-]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*(\/?)>|([^<]+)/g;
    for (let m; (m = re.exec(html)); ) {
      const top = stack[stack.length - 1];
      if (m[5] !== undefined) { if (m[5]) top.childNodes.push(adopt(top, new Text(decode(m[5])))); }
      else if (m[2]) {
        const el = new (BUILTIN[m[2].toLowerCase()] || Plain)(m[2].toLowerCase());
        for (const a of m[3].matchAll(/([^\s=>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) el._attrs.set(a[1].toLowerCase(), decode(a[2] ?? a[3] ?? a[4] ?? ""));
        top.childNodes.push(adopt(top, el));
        if (!VOID.has(el.localName) && !m[4]) stack.push(el);
      } else if (m[1]) {
        const i = stack.map((s) => s.localName).lastIndexOf(m[1].toLowerCase());
        if (i > 0) stack.length = i;
      }
    }
    const kids = root.childNodes;
    for (const k of kids) k.parentNode = null;
    return kids;
  }
  const adopt = (parent, node) => { node.parentNode = parent; return node; };

  // ---- document, window ----
  const document = new (class Document extends Node {
    constructor() { super(); this._active = null; }
    get nodeType() { return NODE.DOCUMENT; }
    get isConnected() { return true; }
    createElement(name) { return makeElement(name); }
    createTextNode(s) { return new Text(s); }
    getElementById(id) { return this.documentElement.querySelector(`#${id}`); }
    querySelector(sel) { return this.documentElement.querySelector(sel); }
    querySelectorAll(sel) { return this.documentElement.querySelectorAll(sel); }
    _eventParent() { return win; }
  })();
  document.documentElement = new Plain("html");
  document.head = new Plain("head");
  document.body = new Plain("body");
  document.childNodes.push(document.documentElement);
  document.documentElement.parentNode = document;
  document.documentElement.childNodes.push(document.head, document.body);
  document.head.parentNode = document.body.parentNode = document.documentElement;
  Object.defineProperty(document, "activeElement", { // an active element that left the tree is body again
    get() { return this._active && this._active.isConnected ? this._active : this.body; }, set(v) { this._active = v; }, configurable: true,
  });

  const location = {
    _url: new URL(url),
    get href() { return this._url.href; },
    set href(v) {
      const next = new URL(v, this._url);
      const hashOnly = next.href.split("#")[0] === this._url.href.split("#")[0];
      const changed = next.hash !== this._url.hash;
      dom.navigations.push(next.href);
      if (hashOnly) { this._url = next; if (changed) win.dispatchEvent(new Event("hashchange")); }
    },
    get hash() { return this._url.hash === "#" ? "" : this._url.hash; },
    set hash(v) { this.href = "#" + String(v).replace(/^#/, ""); },
    get pathname() { return this._url.pathname; },
    get search() { return this._url.search; },
    assign(v) { this.href = v; },
  };

  const customElements = {
    define(name, cls) {
      if (!/^[a-z][a-z0-9._]*-[a-z0-9._-]*$/.test(name)) throw new Error(`dom-stub: SyntaxError, "${name}" is not a valid custom element name`);
      if (registry.has(name)) throw new Error(`dom-stub: NotSupportedError, "${name}" is already defined`);
      if (byClass.has(cls)) throw new Error("dom-stub: NotSupportedError, this constructor is already used for another element");
      registry.set(name, { cls, observed: [...(cls.observedAttributes || [])].map((s) => s.toLowerCase()) });
      byClass.set(cls, name);
      for (const e of document.documentElement._descendants()) if (e.localName === name) { e._upgrade(); e._conn = false; e._connect(); }
    },
    get: (name) => registry.get(name)?.cls,
    whenDefined: (name) => Promise.resolve(registry.get(name)?.cls),
  };

  const win = {
    document, location, customElements, HTMLElement, Element, Node, Text, Event, CustomEvent, KeyboardEvent, MouseEvent,
    HTMLButtonElement, HTMLInputElement, HTMLAnchorElement, HTMLDialogElement,
    queueMicrotask, setTimeout, clearTimeout, setInterval, clearInterval, console, URL, Promise,
    _eventParent: () => null,
  };
  win.window = win.self = win.globalThis = win;
  Object.assign(win, Object.fromEntries(Object.entries(targetMixin)));
  const context = vm.createContext(win);

  // ---- test helpers ----
  const dom = {
    window: win, document, location, context, errors, navigations: [],
    /** Runs a script in the page (a classic script: its `window.x = ...` and top-level vars land here). */
    load(src, filename = "page.js") { vm.runInContext(src, context, { filename }); return dom; },
    /** Puts markup in <body> (appended) and returns its elements. Custom elements upgrade as they connect. */
    mount(html, parent = document.body) {
      const kids = parseInto(html);
      parent.append(...kids);
      return kids.length === 1 ? kids[0] : kids;
    },
    /** Dispatches a click like a person's (disabled controls ignore it; a link follows its href). */
    click(el) { el.click(); return dom; },
    /** One key press on `el` (default: the focused element): keydown, its default action, keyup. */
    key(key, { on = document.activeElement, ...mods } = {}) {
      const down = new KeyboardEvent("keydown", { key, ...mods });
      const go = on.dispatchEvent(down);
      if (go) {
        const tag = on.localName;
        const clickable = tag === "button" || (tag === "a" && on.hasAttribute("href"));
        if (key === "Enter" && clickable) on.click();
        else if (key === "Escape") {
          const dlg = document.documentElement.querySelectorAll("dialog").find((d) => d.open && d.modal);
          if (dlg && dlg.dispatchEvent(new Event("cancel", { cancelable: true }))) dlg.close();
        }
      }
      on.dispatchEvent(new KeyboardEvent("keyup", { key, ...mods }));
      if (go && key === " " && on.localName === "button") on.click();
      return dom;
    },
    /** Types text into an input: the value grows one character at a time, "input" fires for each. */
    type(input, text) {
      input.focus();
      for (const ch of text) {
        const go = input.dispatchEvent(new KeyboardEvent("keydown", { key: ch }));
        if (!go) continue;
        input.value = input.value + ch;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
      return dom;
    },
    /** Lets microtasks and promise continuations run. */
    async settle() { for (let i = 0; i < 3; i++) await new Promise((r) => setImmediate(r)); },
    serialize,
    /** Visible text of an element as one line (hidden subtrees are skipped). */
    text(el) {
      const walk = (n) => (n.nodeType === NODE.TEXT ? n.data : n.hasAttribute("hidden") ? "" : n.childNodes.map(walk).join(" "));
      return walk(el).replace(/\s+/g, " ").trim();
    },
  };
  return dom;
}
