import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  z: number;
  baseX: number;
  baseY: number;
  size: number;
  color: string;
  vx: number;
  vy: number;
  vz: number;
  pulse: number;
  pulseSpeed: number;
  isBurst?: boolean;
  life?: number;
  maxLife?: number;
}

export function Canvas3DBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener("resize", handleResize);

    const mouse = { x: width / 2, y: height / 2, targetX: width / 2, targetY: height / 2 };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
    };
    window.addEventListener("mousemove", handleMouseMove);

    const colors = [
      "rgba(56, 189, 248, ",  // cyan
      "rgba(192, 132, 252, ", // purple
      "rgba(244, 114, 182, ", // pink
      "rgba(96, 165, 250, ",  // blue
      "rgba(45, 212, 191, ",  // teal
      "rgba(251, 191, 36, ",  // gold
    ];

    const count = Math.min(Math.floor((width * height) / 14000), 85);
    const particles: Particle[] = [];

    for (let i = 0; i < count; i++) {
      const x = (Math.random() - 0.5) * width * 1.5;
      const y = (Math.random() - 0.5) * height * 1.5;
      const z = Math.random() * 800 + 100;
      particles.push({
        x,
        y,
        z,
        baseX: x,
        baseY: y,
        size: Math.random() * 2.5 + 1,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        vz: (Math.random() - 0.5) * 0.5,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.02 + Math.random() * 0.03,
      });
    }

    // Spawn 3D sparkle bursts on mouse click
    const handleClick = (e: MouseEvent) => {
      const clickX = e.clientX - width / 2;
      const clickY = e.clientY - height / 2;
      
      for (let i = 0; i < 24; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 6 + 2;
        particles.push({
          x: clickX,
          y: clickY,
          z: Math.random() * 200 + 100,
          baseX: clickX,
          baseY: clickY,
          size: Math.random() * 3 + 2,
          color: colors[Math.floor(Math.random() * colors.length)],
          vx: Math.cos(angle) * speed * 25,
          vy: Math.sin(angle) * speed * 25,
          vz: (Math.random() - 0.5) * 10,
          pulse: 0,
          pulseSpeed: 0.1,
          isBurst: true,
          life: 0,
          maxLife: Math.random() * 40 + 30,
        });
      }
    };
    window.addEventListener("click", handleClick);

    const fov = 400;

    const render = () => {
      // Lerp mouse position
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      ctx.clearRect(0, 0, width, height);

      // Radial background aura
      const grad = ctx.createRadialGradient(
        mouse.x,
        mouse.y,
        0,
        width / 2,
        height / 2,
        Math.max(width, height)
      );
      grad.addColorStop(0, "rgba(30, 27, 75, 0.3)");
      grad.addColorStop(0.5, "rgba(15, 23, 42, 0.45)");
      grad.addColorStop(1, "rgba(6, 8, 18, 0.9)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      const offsetX = (mouse.x - width / 2) * 0.25;
      const offsetY = (mouse.y - height / 2) * 0.25;

      const projected: { px: number; py: number; scale: number; p: Particle; alpha: number }[] = [];

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];

        if (p.isBurst) {
          p.life!++;
          p.x += p.vx;
          p.y += p.vy;
          p.vx *= 0.92;
          p.vy *= 0.92;
          p.vy += 0.15; // slight gravity

          if (p.life! >= p.maxLife!) {
            particles.splice(i, 1);
            continue;
          }
        } else {
          // Move ambient 3d position
          p.x += p.vx;
          p.y += p.vy;
          p.z += p.vz;
          p.pulse += p.pulseSpeed;

          // Wrap boundaries
          if (p.x < -width) p.x = width;
          if (p.x > width) p.x = -width;
          if (p.y < -height) p.y = height;
          if (p.y > height) p.y = -height;
          if (p.z < 50) p.z = 900;
          if (p.z > 900) p.z = 50;
        }

        // Perspective calculation
        const scale = fov / (fov + p.z);
        const px = (p.x + offsetX) * scale + width / 2;
        const py = (p.y + offsetY) * scale + height / 2;

        let alpha = Math.min(1, Math.max(0.1, (1 - p.z / 900) * (0.6 + Math.sin(p.pulse) * 0.4)));
        if (p.isBurst) {
          alpha = (1 - p.life! / p.maxLife!) * 0.95;
        }

        projected.push({ px, py, scale, p, alpha });

        // Draw particle
        ctx.beginPath();
        ctx.arc(px, py, p.size * scale * (p.isBurst ? 1.8 : 1.5), 0, Math.PI * 2);
        ctx.fillStyle = p.color + alpha + ")";
        ctx.shadowBlur = (p.isBurst ? 18 : 12) * scale;
        ctx.shadowColor = p.color + "0.9)";
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // Draw constellation connections between ambient particles
      for (let i = 0; i < projected.length; i++) {
        for (let j = i + 1; j < projected.length; j++) {
          const p1 = projected[i];
          const p2 = projected[j];
          if (p1.p.isBurst || p2.p.isBurst) continue;

          const dx = p1.px - p2.px;
          const dy = p1.py - p2.py;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 135) {
            const lineAlpha = (1 - dist / 135) * 0.22 * p1.alpha * p2.alpha;
            ctx.beginPath();
            ctx.moveTo(p1.px, p1.py);
            ctx.lineTo(p2.px, p2.py);
            ctx.strokeStyle = `rgba(147, 197, 253, ${lineAlpha})`;
            ctx.lineWidth = 0.9 * p1.scale;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("click", handleClick);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        pointerEvents: "none",
        zIndex: 0,
      }}
    />
  );
}
