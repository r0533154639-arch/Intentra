import { Link } from 'react-router-dom';

const gestures = [
  {
    name: 'Single click',
    gesture: 'Briefly pinch your thumb and index finger, then release.',
    behavior:
      'The system waits for the double-click interval to pass before sending a left-click. This delay gives you time to make a second pinch.',
  },
  {
    name: 'Double-click',
    gesture: 'Make two brief pinches within the configured double-click interval.',
    behavior:
      'The pending single click is canceled and one double-click is sent when the second pinch is released.',
  },
  {
    name: 'Right-click',
    gesture: 'Pinch and hold your hand steady, then release after the hold duration.',
    behavior:
      'A right-click is sent on release if the pinch lasted long enough and your hand did not move beyond the movement threshold.',
  },
  {
    name: 'Precise scrolling',
    gesture: 'Pinch, then move your hand gradually while keeping the pinch closed.',
    behavior:
      'Once the movement threshold is reached, vertical hand movement scrolls continuously. Scroll sensitivity controls how much the page moves.',
  },
  {
    name: 'Fast scrolling',
    gesture: 'Pinch, make a quick wrist movement, then release.',
    behavior:
      'If the movement speed and acceleration pass their thresholds, the system sends a short, faster scroll when you release. This gesture is treated as scrolling, not as a click.',
  },
];

export default function GesturesPage() {
  return (
    <section className="page-section">
      <div className="page-heading">
        <span className="eyebrow">How it works</span>
        <h1>Hand gestures</h1>
        <p>
          Use a pinch between your thumb and index finger to activate an action. The system
          classifies each pinch as a click, hold, or scroll based on its duration and hand
          movement.
        </p>
      </div>

      <div className="gesture-grid">
        {gestures.map((item, index) => (
          <article className="gesture-card" key={item.name}>
            <span className="gesture-card-icon" aria-hidden="true">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h2>{item.name}</h2>
            <p><strong>What to do</strong><span>{item.gesture}</span></p>
            <p><strong>What the system does</strong><span>{item.behavior}</span></p>
          </article>
        ))}
      </div>

      <aside className="callout">
        <span className="callout-icon" aria-hidden="true">i</span>
        <p>
          <strong>Make it yours</strong>
          Gesture thresholds are configurable and may need calibration for your camera and
          movement. Visit <Link to="/settings">Settings</Link> to adjust them. A zero
          threshold means gesture control is not configured.
        </p>
      </aside>
    </section>
  );
}
