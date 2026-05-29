import { useEffect, useRef, useState } from "react";

export default function CyberCursor() {
  const dotRef   = useRef(null);
  const ringRef  = useRef(null);
  const trailRef = useRef(null);
  const pos      = useRef({ x: -100, y: -100 });
  const ring     = useRef({ x: -100, y: -100 });
  const clicking = useRef(false);
  const [isPointer, setIsPointer] = useState(false);

  useEffect(() => {
    const onMove = (e) => {
      pos.current = { x: e.clientX, y: e.clientY };

      // Check if hovering interactive element
      const el = document.elementFromPoint(e.clientX, e.clientY);
      if (el) {
        const style = window.getComputedStyle(el).cursor;
        setIsPointer(
          style === "pointer" ||
          el.tagName === "A" ||
          el.tagName === "BUTTON" ||
          el.closest("button") ||
          el.closest("a") ||
          el.getAttribute("role") === "button"
        );
      }

      // Dot follows instantly
      if (dotRef.current) {
        dotRef.current.style.transform =
          `translate(${e.clientX}px, ${e.clientY}px)`;
      }
    };

    const onDown = () => {
      clicking.current = true;
      if (dotRef.current)  dotRef.current.style.transform  += " scale(0.6)";
      if (ringRef.current) ringRef.current.style.transform += " scale(0.7)";
    };
    const onUp = () => {
      clicking.current = false;
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup",   onUp);

    // Smooth ring follows with lag
    let rafId;
    const follow = () => {
      ring.current.x += (pos.current.x - ring.current.x) * 0.12;
      ring.current.y += (pos.current.y - ring.current.y) * 0.12;
      if (ringRef.current) {
        ringRef.current.style.transform =
          `translate(${ring.current.x}px, ${ring.current.y}px)`;
      }
      if (trailRef.current) {
        trailRef.current.style.transform =
          `translate(${ring.current.x}px, ${ring.current.y}px)`;
      }
      rafId = requestAnimationFrame(follow);
    };
    rafId = requestAnimationFrame(follow);

    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup",   onUp);
      cancelAnimationFrame(rafId);
    };
  }, []);

  const color = isPointer ? "#00eeff" : "#00ff88";
  const glow  = isPointer ? "#00eeff99" : "#00ff8899";

  return (
    <>
      <style>{`
        * { cursor: none !important; }

        @keyframes cursorPulse {
          0%, 100% { opacity: 1; transform: translate(var(--cx,0px), var(--cy,0px)) scale(1); }
          50%       { opacity: 0.7; transform: translate(var(--cx,0px), var(--cy,0px)) scale(1.15); }
        }
        @keyframes ringRotate {
          from { rotate: 0deg; }
          to   { rotate: 360deg; }
        }
      `}</style>

      {/* Outer trailing ring */}
      <div
        ref={trailRef}
        style={{
          position: "fixed",
          top: 0, left: 0,
          width: 38, height: 38,
          marginLeft: -19, marginTop: -19,
          pointerEvents: "none",
          zIndex: 999998,
          border: `1px solid ${color}44`,
          borderRadius: "50%",
          transition: "border-color 0.2s",
        }}
      />

      {/* Spinning dashed ring */}
      <div
        ref={ringRef}
        style={{
          position: "fixed",
          top: 0, left: 0,
          width: 24, height: 24,
          marginLeft: -12, marginTop: -12,
          pointerEvents: "none",
          zIndex: 999999,
          borderRadius: "50%",
          border: `1.5px dashed ${color}`,
          boxShadow: `0 0 8px ${glow}, inset 0 0 8px ${color}22`,
          animation: "ringRotate 2s linear infinite",
          transition: "border-color 0.2s, box-shadow 0.2s",
        }}
      />

      {/* Core dot */}
      <div
        ref={dotRef}
        style={{
          position: "fixed",
          top: 0, left: 0,
          width: 6, height: 6,
          marginLeft: -3, marginTop: -3,
          pointerEvents: "none",
          zIndex: 1000000,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 6px 2px ${glow}, 0 0 12px 4px ${color}44`,
          transition: "background 0.2s, box-shadow 0.2s",
        }}
      />

      {/* Crosshair lines */}
      <div
        ref={null}
        style={{
          position: "fixed",
          top: 0, left: 0,
          pointerEvents: "none",
          zIndex: 999997,
        }}
      />
    </>
  );
}
