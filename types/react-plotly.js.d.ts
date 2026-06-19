declare module "react-plotly.js" {
  import type { Component } from "react";
  import type { PlotParams } from "plotly.js";
  const Plot: Component<PlotParams>;
  export default Plot;
}
