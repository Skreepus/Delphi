import { useEffect, useRef, useState } from "react";
import * as Cesium from "cesium";
import type { Satellite } from "../types";

const GREEN = Cesium.Color.fromCssColorString("#4ade80");
const AMBER = Cesium.Color.fromCssColorString("#fcd34d");
const RED = Cesium.Color.fromCssColorString("#fb7185");
const SCRATCH = new Cesium.Color();

const HIGHLIGHT_COLOR = Cesium.Color.fromCssColorString("#ffffff");
const HIGHLIGHT_OUTLINE = Cesium.Color.fromCssColorString("#c9a96e");

function riskColor(score: number): Cesium.Color {
  const t = Math.min(1, Math.max(0, score));
  if (t < 0.5) {
    return Cesium.Color.lerp(GREEN, AMBER, t * 2, SCRATCH).clone();
  }
  return Cesium.Color.lerp(AMBER, RED, (t - 0.5) * 2, SCRATCH).clone();
}

function basePixelSize(rel: number): number {
  return 6 + (rel / 100) * 8;
}

interface GlobeProps {
  satellites: Satellite[];
  selectedId: number | null;
  onSelectSatelliteId: (id: number | null) => void;
  isFullscreen: boolean;
  onToggleFullscreen: () => void;
}

interface TooltipState {
  x: number;
  y: number;
  name: string;
  risk: number;
  band: "low" | "medium" | "high";
}

export function Globe({ satellites, selectedId, onSelectSatelliteId, isFullscreen, onToggleFullscreen }: GlobeProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const pointsRef = useRef<Cesium.PointPrimitiveCollection | null>(null);
  const ringRef = useRef<Cesium.BillboardCollection | null>(null);
  const didZoomRef = useRef(false);
  const selectRef = useRef(onSelectSatelliteId);
  selectRef.current = onSelectSatelliteId;
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const viewer = new Cesium.Viewer(el, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      fullscreenButton: false,
      infoBox: false,
      selectionIndicator: false,
      terrainProvider: new Cesium.EllipsoidTerrainProvider(),
      shouldAnimate: true,
      orderIndependentTranslucency: false,
      msaaSamples: 4,
      contextOptions: {
        webgl: { alpha: false, antialias: true },
      },
    });

    const scene = viewer.scene;
    const globe = scene.globe;

    scene.backgroundColor = Cesium.Color.fromCssColorString("#0d0d0d");

    globe.baseColor = Cesium.Color.fromCssColorString("#111111");
    globe.showGroundAtmosphere = true;
    globe.enableLighting = true;
    globe.depthTestAgainstTerrain = false;
    globe.showWaterEffect = false;

    if (scene.skyAtmosphere) {
      scene.skyAtmosphere.show = true;
      scene.skyAtmosphere.brightnessShift = 0.0;
      scene.skyAtmosphere.hueShift = 0.0;
      scene.skyAtmosphere.saturationShift = 0.05;
    }

    if (scene.sun) scene.sun.show = true;
    if (scene.moon) scene.moon.show = false;
    scene.fog.enabled = false;

    const ssc = scene.screenSpaceCameraController;
    ssc.minimumZoomDistance = 1_800_000;
    ssc.maximumZoomDistance = 60_000_000;
    ssc.enableTilt = true;
    ssc.inertiaZoom = 0.65;
    ssc.inertiaSpin = 0.9;
    ssc.inertiaTranslate = 0.9;

    if ("zoomToCursor" in ssc) {
      (ssc as any).zoomToCursor = true;
    }

    try {
      viewer.imageryLayers.removeAll();
      const esri = new Cesium.UrlTemplateImageryProvider({
        url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        credit: "Esri, Maxar, Earthstar Geographics",
        minimumLevel: 0,
        maximumLevel: 19,
      });
      const baseLayer = viewer.imageryLayers.addImageryProvider(esri);
      baseLayer.alpha = 1.0;
      baseLayer.brightness = 0.65;
      baseLayer.contrast = 1.2;
      baseLayer.saturation = 0.7;
    } catch {
      /* fall back to globe base color */
    }

    viewer.camera.setView({
      destination: Cesium.Cartesian3.fromDegrees(30, 20, 24_000_000),
      orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-90),
        roll: 0,
      },
    });

    const points = scene.primitives.add(
      new Cesium.PointPrimitiveCollection()
    );
    pointsRef.current = points;

    const rings = scene.primitives.add(
      new Cesium.BillboardCollection()
    );
    ringRef.current = rings;

    viewerRef.current = viewer;

    const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

    handler.setInputAction(
      (click: { position: Cesium.Cartesian2 }) => {
        const picked = scene.pick(click.position);
        if (picked?.primitive && picked.primitive instanceof Cesium.PointPrimitive) {
          const sat = (picked.primitive as any)._delphiSat as Satellite | undefined;
          selectRef.current(sat?.satelliteId ?? null);
        } else {
          selectRef.current(null);
        }
      },
      Cesium.ScreenSpaceEventType.LEFT_CLICK
    );

    handler.setInputAction(
      (move: { endPosition: Cesium.Cartesian2 }) => {
        const picked = scene.pick(move.endPosition);
        if (picked?.primitive && picked.primitive instanceof Cesium.PointPrimitive) {
          const sat = (picked.primitive as any)._delphiSat as Satellite | undefined;
          if (sat) {
            const risk = sat.satelliteRiskScore;
            const band: "low" | "medium" | "high" =
              risk > 0.7 ? "high" : risk > 0.4 ? "medium" : "low";
            setTooltip({
              x: move.endPosition.x,
              y: move.endPosition.y,
              name: sat.name,
              risk,
              band,
            });
            el.style.cursor = "pointer";
          }
        } else {
          setTooltip(null);
          el.style.cursor = "default";
        }
      },
      Cesium.ScreenSpaceEventType.MOUSE_MOVE
    );

    const ro = new ResizeObserver(() => viewer.resize());
    ro.observe(el);

    return () => {
      ro.disconnect();
      handler.destroy();
      viewer.destroy();
      viewerRef.current = null;
      pointsRef.current = null;
      ringRef.current = null;
    };
  }, []);

  useEffect(() => {
    const points = pointsRef.current;
    const viewer = viewerRef.current;
    if (!points || !viewer) return;

    points.removeAll();

    for (const s of satellites) {
      const col = riskColor(s.satelliteRiskScore);
      col.alpha = 1.0;
      const outAlpha = 0.25 + (s.operatorReliabilityScore / 100) * 0.55;
      const sz = basePixelSize(s.operatorReliabilityScore);
      const outW = 2;

      const p = points.add({
        position: Cesium.Cartesian3.fromDegrees(
          s.longitude,
          s.latitude,
          s.altitudeMeters
        ),
        pixelSize: sz,
        color: col,
        outlineColor: Cesium.Color.WHITE.withAlpha(outAlpha),
        outlineWidth: outW,
        scaleByDistance: new Cesium.NearFarScalar(2e6, 1.8, 3.5e7, 0.55),
        translucencyByDistance: new Cesium.NearFarScalar(2e6, 1, 5e7, 0.65),
      });
      (p as any)._delphiSat = s;
      (p as any)._origColor = col.clone();
      (p as any)._origSize = sz;
      (p as any)._origOutline = Cesium.Color.WHITE.withAlpha(outAlpha);
      (p as any)._origOutlineWidth = outW;
    }

    if (satellites.length > 0 && !didZoomRef.current) {
      didZoomRef.current = true;
      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(30, 20, 24_000_000),
        duration: 2.5,
        easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
      });
    }
  }, [satellites]);

  useEffect(() => {
    const points = pointsRef.current;
    const rings = ringRef.current;
    if (!points || !rings) return;

    rings.removeAll();

    const len = points.length;
    for (let i = 0; i < len; i++) {
      const p = points.get(i);
      const sat = (p as any)._delphiSat as Satellite | undefined;
      if (!sat) continue;

      if (selectedId != null && sat.satelliteId === selectedId) {
        const origSz = (p as any)._origSize ?? 8;
        p.pixelSize = Math.max(18, origSz * 2.5);
        p.color = HIGHLIGHT_COLOR.withAlpha(1.0);
        p.outlineColor = HIGHLIGHT_OUTLINE.withAlpha(1.0);
        p.outlineWidth = 5;

        const canvas = document.createElement("canvas");
        const size = 128;
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext("2d")!;
        const cx = size / 2;
        const cy = size / 2;

        const grad = ctx.createRadialGradient(cx, cy, size * 0.08, cx, cy, size * 0.5);
        grad.addColorStop(0, "rgba(255, 255, 255, 0.25)");
        grad.addColorStop(0.3, "rgba(201, 169, 110, 0.2)");
        grad.addColorStop(0.6, "rgba(201, 169, 110, 0.1)");
        grad.addColorStop(1, "rgba(201, 169, 110, 0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, size, size);

        ctx.beginPath();
        ctx.arc(cx, cy, size * 0.38, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(201, 169, 110, 0.8)";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(cx, cy, size * 0.24, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(201, 169, 110, 0.35)";
        ctx.lineWidth = 1;
        ctx.stroke();

        const lineLen = size * 0.12;
        const gap = size * 0.42;
        ctx.strokeStyle = "rgba(201, 169, 110, 0.5)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(cx, cy - gap / 2);
        ctx.lineTo(cx, cy - gap / 2 - lineLen);
        ctx.moveTo(cx, cy + gap / 2);
        ctx.lineTo(cx, cy + gap / 2 + lineLen);
        ctx.moveTo(cx - gap / 2, cy);
        ctx.lineTo(cx - gap / 2 - lineLen, cy);
        ctx.moveTo(cx + gap / 2, cy);
        ctx.lineTo(cx + gap / 2 + lineLen, cy);
        ctx.stroke();

        rings.add({
          position: p.position,
          image: canvas,
          width: 120,
          height: 120,
          scale: 1.0,
          color: Cesium.Color.WHITE,
          scaleByDistance: new Cesium.NearFarScalar(2e6, 3.0, 3.5e7, 0.7),
          translucencyByDistance: new Cesium.NearFarScalar(1.5e6, 1, 5e7, 0.4),
        });
      } else {
        const dimFactor = selectedId != null ? 0.35 : 1.0;
        const origColor = (p as any)._origColor as Cesium.Color;
        if (origColor) {
          p.color = origColor.withAlpha(origColor.alpha * dimFactor);
        }
        p.pixelSize = ((p as any)._origSize ?? 8) * (selectedId != null ? 0.7 : 1.0);
        p.outlineColor = ((p as any)._origOutline as Cesium.Color) ?? Cesium.Color.WHITE.withAlpha(0.1);
        p.outlineWidth = (p as any)._origOutlineWidth ?? 2;
      }
    }
  }, [selectedId, satellites]);

  const handleReset = () => {
    viewerRef.current?.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(30, 20, 24_000_000),
      duration: 1.8,
      easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
    });
  };

  const bandColors = {
    low: "text-emerald-400",
    medium: "text-amber-400",
    high: "text-red-400",
  };

  return (
    <div className="relative h-full w-full overflow-hidden bg-delphi-bg">
      <div ref={containerRef} className="h-full w-full" />

      {/* Vignette */}
      <div
        className="pointer-events-none absolute inset-0 z-[5]"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 55%, rgba(13,13,13,0.5) 100%)",
        }}
      />

      {/* Hover tooltip */}
      {tooltip && (
        <div
          className="pointer-events-none absolute z-20 flex items-center gap-2 rounded-md border border-delphi-border bg-delphi-surface/95 px-3 py-1.5 shadow-xl backdrop-blur-md"
          style={{
            left: tooltip.x + 14,
            top: tooltip.y - 10,
            transform: "translateY(-100%)",
          }}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              tooltip.band === "high"
                ? "bg-red-400"
                : tooltip.band === "medium"
                  ? "bg-amber-400"
                  : "bg-emerald-400"
            }`}
          />
          <span className="text-[11px] font-light tracking-wide text-delphi-text">
            {tooltip.name}
          </span>
          <span className={`font-mono text-[10px] ${bandColors[tooltip.band]}`}>
            {tooltip.risk.toFixed(2)}
          </span>
        </div>
      )}

      {/* Bottom-left HUD */}
      <div className="absolute bottom-4 left-4 z-10 rounded-md border border-delphi-border bg-delphi-bg/80 px-3 py-1.5 font-mono text-[10px] tracking-wider text-delphi-muted/60 shadow-lg backdrop-blur-md">
        {satellites.length.toLocaleString()} targets
      </div>

      {/* Bottom-right controls */}
      <div className="absolute bottom-4 right-4 z-10 flex items-center gap-2">
        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 rounded-md border border-delphi-border bg-delphi-bg/80 px-3 py-2 text-[10px] font-light uppercase tracking-[0.2em] text-delphi-muted shadow-lg backdrop-blur-md transition-all duration-300 hover:border-delphi-accent/30 hover:text-delphi-accent"
          title="Reset camera"
        >
          <svg
            className="h-3 w-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            <circle cx="12" cy="12" r="10" />
          </svg>
          Reset
        </button>

        <button
          onClick={onToggleFullscreen}
          className="flex items-center gap-1.5 rounded-md border border-delphi-border bg-delphi-bg/80 px-3 py-2 text-[10px] font-light uppercase tracking-[0.2em] text-delphi-muted shadow-lg backdrop-blur-md transition-all duration-300 hover:border-delphi-accent/30 hover:text-delphi-accent"
          title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
        >
          {isFullscreen ? (
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
            </svg>
          ) : (
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
            </svg>
          )}
          {isFullscreen ? "Exit" : "Expand"}
        </button>
      </div>
    </div>
  );
}
