// @ts-nocheck
"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

type Props = {
  data: object;
  className?: string;
};

export default function PlotlyChart({ data, className }: Props) {
  const fig = data as { data?: object[]; layout?: object };
  return (
    <div className={className ?? "w-full min-h-[280px]"}>
      <Plot
        data={fig.data ?? []}
        layout={{
          ...(fig.layout ?? {}),
          autosize: true,
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler
      />
    </div>
  );
}
