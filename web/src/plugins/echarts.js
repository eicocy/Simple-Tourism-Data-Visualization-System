let echartsLoader = null;

export function loadEcharts() {
  if (!echartsLoader) {
    echartsLoader = Promise.all([
      import("echarts/core"),
      import("echarts/charts"),
      import("echarts/components"),
      import("echarts/renderers"),
    ]).then(([echarts, charts, components, renderers]) => {
      echarts.use([
        charts.BarChart,
        charts.LineChart,
        charts.MapChart,
        charts.PieChart,
        charts.RadarChart,
        components.GridComponent,
        components.LegendComponent,
        components.RadarComponent,
        components.TitleComponent,
        components.TooltipComponent,
        components.VisualMapComponent,
        renderers.CanvasRenderer,
      ]);

      return echarts;
    });
  }

  return echartsLoader;
}

export default loadEcharts;
