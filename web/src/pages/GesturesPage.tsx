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
    <section style={{ maxWidth: 960, margin: '0 auto' }}>
      <h1>Hand gestures</h1>
      <p>
        Use a pinch between your thumb and index finger to activate an action. The system
        classifies each pinch as a click, hold, or scroll based on its duration and hand
        movement.
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 260px), 1fr))',
          gap: '1rem',
          marginTop: '1.5rem',
        }}
      >
        {gestures.map((item) => (
          <article
            key={item.name}
            style={{
              border: '1px solid #d1d5db',
              borderRadius: 8,
              padding: '1rem',
              background: '#fff',
            }}
          >
            <h2 style={{ marginTop: 0 }}>{item.name}</h2>
            <p><strong>What to do:</strong> {item.gesture}</p>
            <p><strong>What the system does:</strong> {item.behavior}</p>
          </article>
        ))}
      </div>

      <aside
        style={{
          marginTop: '1.5rem',
          padding: '1rem',
          borderLeft: '4px solid #2563eb',
          background: '#eff6ff',
        }}
      >
        <strong>Tip:</strong> Gesture thresholds are configurable and may need calibration
        for your camera and movement. Visit <Link to="/settings">Settings</Link> to adjust
        them. A zero threshold means gesture control is not configured.
      </aside>
    </section>
  );
}
