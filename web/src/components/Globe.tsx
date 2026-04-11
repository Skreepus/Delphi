import { useEffect, useRef } from "react";
import * as Cesium from "cesium";
import type { Satellite } from "../types";

function riskColor(score: number): Cesium.Color {
  const t = Math.min(1, Math.max(0, score));
  return Cesium.Color.lerp(
    Cesium.Color.fromCssColorString("#22c55e"),
    Cesium.Color.fromCssColorString("#ef4444"),
    t,
    new Cesium.Color()
  );
}

function pixelSizeFromReliability(rel: number): number {
  return 3 + (rel / 100) * 12;
}

function outlineFromReliability(rel: number): number {
  return 0.5 + (rel / 100) * 3;
}

interface GlobeProps {
  satellites: Satellite[];
  onSelectSatelliteId: (id: number | null) => void;
}

export function Globe({ satellites, onSelectSatelliteId }: GlobeProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Cesium.Viewer | null>(null);
  const dataSourceRef = useRef<Cesium.CustomDataSource | null>(null);
  const didZoomRef = useRef(false);
  const selectRef = useRef(onSelectSatelliteId);
  selectRef.current = onSelectSatelliteId;

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const viewer = new Cesium.Viewer(el, {
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: true,
      sceneModePicker: true,
      navigationHelpButton: false,
      fullscreenButton: false,
      terrainProvider: new Cesium.EllipsoidTerrainProvider(),
      shouldAnimate: false,
    });

    viewer.scene.backgroundColor =
      Cesium.Color.fromCssColorString("#0d0d0d");
    viewer.scene.globe.showGroundAtmosphere = true;
    viewer.scene.globe.baseColor =
      Cesium.Color.fromCssColorString("#161616");
    if (viewer.scene.skyAtmosphere) {
      viewer.scene.skyAtmosphere.show = true;
    }

    try {
      const osm = new Cesium.UrlTemplateImageryProvider({
        url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      });
      viewer.imageryLayers.addImageryProvider(osm);
    } catch {
      /* optional */
    }

    const ds = new Cesium.CustomDataSource("delphi-satellites");
    viewer.dataSources.add(ds);
    dataSourceRef.current = ds;
    viewerRef.current = viewer;

    const onSelected = () => {
      const e = viewer.selectedEntity;
      if (!e?.id) {
        selectRef.current(null);
        return;
      }
      const raw = e.id;
      const num =
        typeof raw === "string" ? parseInt(raw, 10) : Number(raw);
      if (Number.isFinite(num)) selectRef.current(num);
      else selectRef.current(null);
    };
    viewer.selectedEntityChanged.addEventListener(onSelected);

    const resize = () => {
      viewer.resize();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(el);
    window.addEventListener("orientationchange", resize);

    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((click: { position: Cesium.Cartesian2 }) => {
      const picked = viewer.scene.pick(click.position);
      if (
        Cesium.defined(picked) &&
        picked.id instanceof Cesium.Entity
      ) {
        viewer.selectedEntity = picked.id;
      } else {
        viewer.selectedEntity = undefined;
        selectRef.current(null);
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    return () => {
      ro.disconnect();
      window.removeEventListener("orientationchange", resize);
      handler.destroy();
      viewer.selectedEntityChanged.removeEventListener(onSelected);
      viewer.destroy();
      viewerRef.current = null;
      dataSourceRef.current = null;
    };
  }, []);

  useEffect(() => {
    const viewer = viewerRef.current;
    const ds = dataSourceRef.current;
    if (!viewer || !ds) return;

    ds.entities.removeAll();

    for (const s of satellites) {
      const pos = Cesium.Cartesian3.fromDegrees(
        s.longitude,
        s.latitude,
        s.altitudeMeters
      );
      const rel = s.operatorReliabilityScore;
      const risk = s.satelliteRiskScore;
      const col = riskColor(risk);
      const outline = Cesium.Color.WHITE.withAlpha(0.15 + (rel / 100) * 0.55);

      ds.entities.add({
        id: String(s.satelliteId),
        name: s.name,
        position: pos,
        point: {
          pixelSize: pixelSizeFromReliability(rel),
          color: col,
          outlineColor: outline,
          outlineWidth: outlineFromReliability(rel),
        },
      });
    }

    if (satellites.length > 0 && !didZoomRef.current) {
      didZoomRef.current = true;
      viewer.zoomTo(ds).catch(() => {
        /* ignore */
      });
    }
  }, [satellites]);

  return (
    <div
      ref={containerRef}
      className="h-full w-full min-h-[240px] rounded-sm border border-delphi-border/90"
    />
  );
}
