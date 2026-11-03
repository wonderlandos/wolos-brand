# Atlas: motion

Atlas moves on the shell's motion table and nothing else. The table is hig.md section 7, "Motion" (durations, curves, springs, stagger, the clock). Status of that source: it is written on the branch `wave3/desktop-int` (worktree `wt/fix-comp`, `docs/modules/hig.md` lines 79 to 146) and is not in `split/wolos` main yet; the code it names is `crates/shell/src/kit/motion.rs`, `crates/wolkit/src/style/value.rs` (`Ease`) and `crates/wolkit/src/anim/mod.rs` (`DURATIONS_NS`). The wolkit style tokens `--motion-fast` 150 ms, `--motion-normal` 250 ms, `--motion-slow` 400 ms and `--ease` are on main (wolkit-style.md, Scales). Where the two differ, the table in the branch wins and this note follows it.

Motion says where a thing came from and where it went. It never makes the person wait: nothing runs longer than 400 ms, and nothing waits on an animation to accept input. Atlas is the app where the person is waiting for the web already; its own chrome adds no delay to that.

## 1. The rules, short

- Durations: `fast` 150 ms for hover, press, toggles and anything leaving; `normal` 250 ms for panels, popovers, list rows entering; `slow` 400 ms for large surfaces.
- Enter with `ease` (cubic-bezier .2, .8, .2, 1); leave with `in` (.4, 0, 1, 1) one step faster: a panel opens in 250 ms and closes in 150 ms. `linear` only for value-driven fades and progress, never for movement.
- Springs (`gentle`, `snappy`, `bouncy`) are for things the hand moved and lets go. A click or a hover is a curve.
- CSS moves `transform` and `opacity` only, never margins, padding, width or height (a margin per frame relayouts the window).
- Interruptible: a second hover or a tab closing mid-open turns the value round from where it is.
- Reduce motion (Accessibility > Reduce motion): every move jumps to its end state at once, stagger delays are ignored, progress values still update. The end state is identical; only the frames between go.

## 2. Atlas events

| Event | Motion | Duration and curve |
|---|---|---|
| Hover on a toolbar button, a tab row, a suggestion | fill fades to `control` | `fast`, `ease` |
| Press | fill to accent tint, no scale | `fast`, `ease` |
| Omnibox gets focus | the 2 px `accent` ring fades in (opacity only) | `fast`, `ease`; leaves with `in` |
| Omnibox suggestions open | popover fades in and moves up 4 px (`transform`) | `normal`, `ease` in; `fast`, `in` out |
| Page loading | bar along the omnibox bottom follows the load value; after 150 ms with no value, a Spinner in the glyph slot | `linear`, value-driven; the page you are leaving stays on screen until the new one paints (never a blank pane) |
| Page switch (tab selected) | none: the page changes at once. The selection pill moves to the new row. | pill: `fast`, `ease`; content: instant |
| New tab opens | the new row fades in and moves 8 px from the left; the rows below reflow once, not per frame; the page appears at once | `normal`, `ease` |
| Tab closes | the row fades out; the rows below close the gap at the end of the fade (one reflow) | `fast`, `in` |
| Tab dragged and dropped | the row follows the pointer, then settles into its slot | spring `snappy` (230 ms settle) |
| Sidebar hide / show (Super+Alt+S) | the sidebar slides by `transform`; the page resizes once, at the start of a hide and at the end of a show | show `normal`, `ease`; hide `fast`, `in` |
| Menu and popover (the `open-menu` menu, a tab's context menu) | fades in with a 4 px rise | `normal`, `ease` in; `fast`, `in` out |
| Download starts | the toolbar button's ring appears and fills; no popup | `fast`, `ease`; fill `linear` by value |
| Do Not Track toggled | the glyph colour changes; nothing moves | `fast`, `ease` |
| New tab page appears | heading, search field, "Pinned" and "Pick up where you left off" enter one after another, 30 ms apart, 8 px rise and fade; only the first time the page opens in a window, not on each focus | `normal`, `ease`; `Stagger::GAP_MS` 30, spread capped at 300 ms; leaves last first |
| First run opens | the card enters, then its rows stagger | card: `slow`, `ease`; rows: `normal`, `ease`, 30 ms apart |
| First run done ("Start browsing") | the card fades out; the new tab page enters as above | card: `fast`, `in`; page: `normal`, `ease` |
| Window open / close | the compositor's springs `window-open` (200 ms settle) and `window-close` (240 ms). Atlas animates nothing of its own here. | spring, compositor |
| Launch | no splash, no logo animation. The window opens on the last session or on the new tab page. | none |

## 3. What does not move

- The logo. It does not animate at launch, on the first run, on the new tab page or in the About dialog. The first thing Atlas shows is the page.
- The page content. Atlas never animates or fades the web page it hosts, and does not smooth-scroll beyond what the engine does.
- Counters, favicons and loading dots do not pulse to ask for attention. A tab that has news changes its title weight, once.
- A tab does not bounce, shake or wobble. The lock-screen shake and the Dock bounce are the shell's own gestures for "no" and "look here"; a browser has no business using them.

## 4. How it is held

- Native chrome goes through `kit::anim::Animated` on the window's one clock, with `retarget` for interruptions and `connect_settled` to hide a closed popover (hig.md section 7).
- Internal pages (new tab, first run) use CSS with `--motion-fast`, `--motion-normal`, `--motion-slow`, `--ease`, transform and opacity only, and honour `@media (prefers-reduced-motion: reduce)`. Whether the portal maps the shell's Reduce motion setting to that media query is [verify]; if it does not, the page reads the setting from the shell and applies the same rule.
- Goldens: the first-run and new-tab frames are tested at the end state, with `Clock::manual()` and `clock.step(now_ns)` for the middle, and with `clock.set_reduced(Some(true))` for the reduced path.
- WK-004 (a transition over 500 ms) and RU-060 apply to Atlas's own CSS like any other: no row of this table is over 400 ms.
