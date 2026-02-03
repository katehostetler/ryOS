import { motion } from "framer-motion";
import type { WeatherType } from "../../types/weather";

// Size configurations
type SizeType = "small" | "medium" | "large";

const SIZES: Record<SizeType, { width: number; height: number }> = {
  small: { width: 32, height: 32 },
  medium: { width: 56, height: 56 },
  large: { width: 100, height: 100 },
};

interface IconProps {
  size: SizeType;
  animated: boolean;
}

// Sunny icon - warm sun with animated rays
function SunnyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <radialGradient id="sunGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FEF08A" />
          <stop offset="40%" stopColor="#FCD34D" />
          <stop offset="70%" stopColor="#FBBF24" />
          <stop offset="100%" stopColor="#F59E0B" />
        </radialGradient>
        <radialGradient id="sunCore" cx="50%" cy="40%" r="50%">
          <stop offset="0%" stopColor="#FEF9C3" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
        <filter id="sunGlow">
          <feGaussianBlur stdDeviation="3" result="glow" />
          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Sun rays */}
      <motion.g
        filter="url(#sunGlow)"
        animate={animated ? { rotate: 360 } : {}}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        style={{ transformOrigin: "50px 50px" }}
      >
        {[...Array(12)].map((_, i) => (
          <motion.rect
            key={i}
            x="48"
            y="5"
            width="4"
            height="14"
            rx="2"
            fill="#FBBF24"
            style={{ transformOrigin: "50px 50px" }}
            transform={`rotate(${i * 30})`}
            animate={animated ? { opacity: [0.6, 1, 0.6] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </motion.g>

      {/* Main sun body */}
      <circle cx="50" cy="50" r="28" fill="url(#sunGradient)" filter="url(#sunGlow)" />

      {/* Sun highlight */}
      <ellipse cx="42" cy="42" rx="10" ry="8" fill="url(#sunCore)" opacity="0.8" />
    </svg>
  );
}

// Partly cloudy - sun peeking behind cloud
function PartlyCloudyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <radialGradient id="pcSunGradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FEF08A" />
          <stop offset="70%" stopColor="#FBBF24" />
          <stop offset="100%" stopColor="#F59E0B" />
        </radialGradient>
        <linearGradient id="pcCloudGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="50%" stopColor="#F1F5F9" />
          <stop offset="100%" stopColor="#CBD5E1" />
        </linearGradient>
        <filter id="cloudShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.2" />
        </filter>
      </defs>

      {/* Sun behind cloud */}
      <motion.g
        animate={animated ? { scale: [1, 1.05, 1] } : {}}
        transition={{ duration: 3, repeat: Infinity }}
        style={{ transformOrigin: "30px 30px" }}
      >
        <circle cx="30" cy="30" r="18" fill="url(#pcSunGradient)" />
        {/* Sun rays (partial) */}
        {[...Array(5)].map((_, i) => (
          <rect
            key={i}
            x="28"
            y="5"
            width="4"
            height="10"
            rx="2"
            fill="#FBBF24"
            style={{ transformOrigin: "30px 30px" }}
            transform={`rotate(${-60 + i * 30})`}
            opacity="0.8"
          />
        ))}
      </motion.g>

      {/* Cloud */}
      <motion.g
        filter="url(#cloudShadow)"
        animate={animated ? { x: [-2, 2, -2] } : {}}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <ellipse cx="55" cy="65" rx="30" ry="18" fill="url(#pcCloudGradient)" />
        <ellipse cx="40" cy="58" rx="18" ry="14" fill="url(#pcCloudGradient)" />
        <ellipse cx="65" cy="55" rx="20" ry="16" fill="url(#pcCloudGradient)" />
        <ellipse cx="52" cy="50" rx="16" ry="12" fill="#FFFFFF" />
      </motion.g>
    </svg>
  );
}

// Cloudy icon - overcast clouds
function CloudyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <linearGradient id="cloudGradientBack" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#94A3B8" />
          <stop offset="100%" stopColor="#64748B" />
        </linearGradient>
        <linearGradient id="cloudGradientFront" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#F8FAFC" />
          <stop offset="50%" stopColor="#E2E8F0" />
          <stop offset="100%" stopColor="#CBD5E1" />
        </linearGradient>
        <filter id="cloudyShadow">
          <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25" />
        </filter>
      </defs>

      {/* Back cloud */}
      <motion.g
        animate={animated ? { x: [0, 3, 0] } : {}}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
      >
        <ellipse cx="35" cy="40" rx="22" ry="16" fill="url(#cloudGradientBack)" />
        <ellipse cx="55" cy="35" rx="18" ry="14" fill="url(#cloudGradientBack)" />
      </motion.g>

      {/* Front cloud */}
      <motion.g
        filter="url(#cloudyShadow)"
        animate={animated ? { x: [-2, 2, -2] } : {}}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
      >
        <ellipse cx="50" cy="62" rx="32" ry="20" fill="url(#cloudGradientFront)" />
        <ellipse cx="32" cy="55" rx="20" ry="16" fill="url(#cloudGradientFront)" />
        <ellipse cx="68" cy="52" rx="22" ry="18" fill="url(#cloudGradientFront)" />
        <ellipse cx="50" cy="48" rx="18" ry="14" fill="#FFFFFF" />
      </motion.g>
    </svg>
  );
}

// Rainy icon - cloud with rain drops
function RainyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <linearGradient id="rainCloudGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#94A3B8" />
          <stop offset="50%" stopColor="#64748B" />
          <stop offset="100%" stopColor="#475569" />
        </linearGradient>
        <linearGradient id="rainDropGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#60A5FA" />
          <stop offset="100%" stopColor="#3B82F6" />
        </linearGradient>
        <filter id="rainCloudShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3" />
        </filter>
      </defs>

      {/* Cloud */}
      <g filter="url(#rainCloudShadow)">
        <ellipse cx="50" cy="35" rx="30" ry="18" fill="url(#rainCloudGradient)" />
        <ellipse cx="30" cy="30" rx="18" ry="14" fill="url(#rainCloudGradient)" />
        <ellipse cx="68" cy="28" rx="20" ry="16" fill="url(#rainCloudGradient)" />
        <ellipse cx="50" cy="24" rx="14" ry="10" fill="#64748B" />
      </g>

      {/* Rain drops */}
      {[
        { x: 30, delay: 0 },
        { x: 45, delay: 0.3 },
        { x: 60, delay: 0.6 },
        { x: 38, delay: 0.15 },
        { x: 52, delay: 0.45 },
        { x: 68, delay: 0.75 },
      ].map((drop, i) => (
        <motion.ellipse
          key={i}
          cx={drop.x}
          cy="55"
          rx="2.5"
          ry="6"
          fill="url(#rainDropGradient)"
          animate={
            animated
              ? {
                  y: [0, 35],
                  opacity: [1, 0.3],
                }
              : {}
          }
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: drop.delay,
            ease: "easeIn",
          }}
        />
      ))}
    </svg>
  );
}

// Stormy icon - dark cloud with lightning
function StormyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <linearGradient id="stormCloudGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#475569" />
          <stop offset="50%" stopColor="#334155" />
          <stop offset="100%" stopColor="#1E293B" />
        </linearGradient>
        <linearGradient id="lightningGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FEF08A" />
          <stop offset="50%" stopColor="#FCD34D" />
          <stop offset="100%" stopColor="#FBBF24" />
        </linearGradient>
        <filter id="lightningGlow">
          <feGaussianBlur stdDeviation="2" result="glow" />
          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="stormShadow">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.4" />
        </filter>
      </defs>

      {/* Dark cloud */}
      <g filter="url(#stormShadow)">
        <ellipse cx="50" cy="32" rx="32" ry="20" fill="url(#stormCloudGradient)" />
        <ellipse cx="28" cy="28" rx="20" ry="16" fill="url(#stormCloudGradient)" />
        <ellipse cx="72" cy="26" rx="22" ry="18" fill="url(#stormCloudGradient)" />
        <ellipse cx="50" cy="22" rx="16" ry="12" fill="#334155" />
      </g>

      {/* Lightning bolt */}
      <motion.g
        filter="url(#lightningGlow)"
        animate={
          animated
            ? {
                opacity: [0, 1, 1, 0, 0, 1, 0],
                scale: [0.95, 1, 1, 0.95, 0.95, 1, 0.95],
              }
            : { opacity: 1 }
        }
        transition={{
          duration: 2,
          repeat: Infinity,
          times: [0, 0.1, 0.15, 0.2, 0.8, 0.85, 1],
        }}
        style={{ transformOrigin: "50px 65px" }}
      >
        <path d="M55 48 L48 62 L54 62 L46 82 L58 65 L52 65 L60 48 Z" fill="url(#lightningGradient)" />
      </motion.g>

      {/* Rain drops */}
      {[
        { x: 30, delay: 0 },
        { x: 70, delay: 0.4 },
      ].map((drop, i) => (
        <motion.ellipse
          key={i}
          cx={drop.x}
          cy="55"
          rx="2"
          ry="5"
          fill="#64748B"
          animate={
            animated
              ? {
                  y: [0, 33],
                  opacity: [0.7, 0.2],
                }
              : {}
          }
          transition={{
            duration: 0.7,
            repeat: Infinity,
            delay: drop.delay,
            ease: "easeIn",
          }}
        />
      ))}
    </svg>
  );
}

// Foggy icon - layered mist
function FoggyIcon({ size, animated }: IconProps) {
  const { width, height } = SIZES[size];

  return (
    <svg width={width} height={height} viewBox="0 0 100 100" fill="none">
      <defs>
        <linearGradient id="fogGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#E2E8F0" stopOpacity="0.3" />
          <stop offset="50%" stopColor="#CBD5E1" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#E2E8F0" stopOpacity="0.3" />
        </linearGradient>
      </defs>

      {/* Fog layers */}
      {[
        { y: 30, width: 60, delay: 0 },
        { y: 42, width: 70, delay: 0.5 },
        { y: 54, width: 55, delay: 1 },
        { y: 66, width: 65, delay: 1.5 },
      ].map((layer, i) => (
        <motion.rect
          key={i}
          x={(100 - layer.width) / 2}
          y={layer.y}
          width={layer.width}
          height="8"
          rx="4"
          fill="url(#fogGradient)"
          animate={
            animated
              ? {
                  x: [(100 - layer.width) / 2 - 5, (100 - layer.width) / 2 + 5, (100 - layer.width) / 2 - 5],
                  opacity: [0.6, 0.9, 0.6],
                }
              : {}
          }
          transition={{
            duration: 3 + i * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: layer.delay,
          }}
        />
      ))}

      {/* Lighter fog wisps */}
      {[
        { y: 36, width: 40, x: 10 },
        { y: 48, width: 35, x: 55 },
        { y: 60, width: 45, x: 5 },
      ].map((wisp, i) => (
        <motion.rect
          key={`wisp-${i}`}
          x={wisp.x}
          y={wisp.y}
          width={wisp.width}
          height="4"
          rx="2"
          fill="#F1F5F9"
          opacity="0.5"
          animate={
            animated
              ? {
                  x: [wisp.x, wisp.x + 10, wisp.x],
                }
              : {}
          }
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.7,
          }}
        />
      ))}
    </svg>
  );
}

// Icon component map
const ICONS: Record<WeatherType, React.FC<IconProps>> = {
  sunny: SunnyIcon,
  partly_cloudy: PartlyCloudyIcon,
  cloudy: CloudyIcon,
  rainy: RainyIcon,
  stormy: StormyIcon,
  foggy: FoggyIcon,
};

// Main WeatherIcon component
interface WeatherIconProps {
  weather?: WeatherType;
  size?: SizeType;
  animated?: boolean;
}

export default function WeatherIcon({ weather = "foggy", size = "medium", animated = true }: WeatherIconProps) {
  const IconComponent = ICONS[weather] || ICONS.foggy;

  return (
    <div className="weather-icon-wrapper" style={{ display: "inline-flex" }}>
      <IconComponent size={size} animated={animated} />
    </div>
  );
}
