import React, { useState, useRef, MouseEvent } from "react";

interface Tilt3DProps {
  children: React.ReactNode;
  className?: string;
  maxTilt?: number;
  perspective?: number;
  style?: React.CSSProperties;
}

export function Tilt3D({
  children,
  className = "",
  maxTilt = 10,
  perspective = 1000,
  style = {},
}: Tilt3DProps) {
  const cardRef = useRef<HTMLDivElement | null>(null);
  const [transform, setTransform] = useState<string>("perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)");
  const [glowStyle, setGlowStyle] = useState<React.CSSProperties>({ opacity: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateY = ((x - centerX) / centerX) * maxTilt;
    const rotateX = -((y - centerY) / centerY) * maxTilt;

    setTransform(
      `perspective(${perspective}px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.015, 1.015, 1.015)`
    );

    const glowX = (x / rect.width) * 100;
    const glowY = (y / rect.height) * 100;

    setGlowStyle({
      opacity: 0.85,
      background: `radial-gradient(circle at ${glowX}% ${glowY}%, rgba(255, 255, 255, 0.12) 0%, rgba(99, 102, 241, 0.05) 40%, transparent 80%)`,
    });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTransform(`perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`);
    setGlowStyle({ opacity: 0 });
  };

  return (
    <div
      ref={cardRef}
      className={`tilt-3d-wrapper ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        transform,
        transition: isHovered ? "transform 0.08s ease-out" : "transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)",
        transformStyle: "preserve-3d",
        position: "relative",
        willChange: "transform",
        ...style,
      }}
    >
      {children}
      {/* Glossy light sheen overlay */}
      <div
        className="tilt-3d-glow"
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "inherit",
          pointerEvents: "none",
          transition: "opacity 0.3s ease",
          zIndex: 10,
          ...glowStyle,
        }}
      />
    </div>
  );
}
