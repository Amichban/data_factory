/**
 * Candlestick Chart Component
 * 
 * Interactive chart showing candlestick data with resistance events overlay
 */

import React, { useMemo, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { ResistanceEvent } from '@/lib/api/events';
import { chartConfig } from '@/lib/config';
import { format } from 'date-fns';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface CandleData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface CandlestickChartProps {
  candles: CandleData[];
  events?: ResistanceEvent[];
  selectedEvent?: ResistanceEvent | null;
  height?: number;
  showVolume?: boolean;
  instrument?: string;
  timeframe?: string;
  onEventClick?: (event: ResistanceEvent) => void;
  className?: string;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  candles,
  events = [],
  selectedEvent,
  height = 400,
  showVolume = false,
  instrument = 'EUR_USD',
  timeframe = 'H1',
  onEventClick,
  className = '',
}) => {
  const chartRef = useRef<any>(null);

  // Prepare candlestick data
  const candlestickTrace = useMemo(() => {
    if (!candles || candles.length === 0) return null;

    return {
      type: 'candlestick',
      x: candles.map(c => c.timestamp),
      open: candles.map(c => c.open),
      high: candles.map(c => c.high),
      low: candles.map(c => c.low),
      close: candles.map(c => c.close),
      name: 'Price',
      increasing: chartConfig.candlestick.increasing,
      decreasing: chartConfig.candlestick.decreasing,
      hovertemplate: 
        '<b>%{x}</b><br>' +
        'Open: %{open}<br>' +
        'High: %{high}<br>' +
        'Low: %{low}<br>' +
        'Close: %{close}<br>' +
        '<extra></extra>',
    };
  }, [candles]);

  // Prepare resistance levels from events
  const resistanceLines = useMemo(() => {
    const levels = new Map<number, { count: number; events: ResistanceEvent[] }>();
    
    events.forEach(event => {
      const level = Math.round(event.resistance_level * 10000) / 10000; // Round to 4 decimals
      if (!levels.has(level)) {
        levels.set(level, { count: 0, events: [] });
      }
      const data = levels.get(level)!;
      data.count++;
      data.events.push(event);
    });

    return Array.from(levels.entries()).map(([level, data]) => ({
      type: 'scatter',
      mode: 'lines',
      x: [candles[0]?.timestamp, candles[candles.length - 1]?.timestamp],
      y: [level, level],
      name: `Resistance ${level.toFixed(4)}`,
      line: {
        color: chartConfig.resistance.color,
        width: Math.min(data.count * 0.5 + 1, 3), // Thicker lines for more frequent levels
        dash: chartConfig.resistance.dash,
      },
      hovertemplate: 
        `<b>Resistance Level: ${level.toFixed(4)}</b><br>` +
        `Events: ${data.count}<br>` +
        '<extra></extra>',
      customdata: data.events,
    }));
  }, [events, candles]);

  // Prepare event markers
  const eventMarkers = useMemo(() => {
    if (!events || events.length === 0) return null;

    const resistanceEvents = events.filter(e => e.event_type === 'resistance_bounce');
    const supportEvents = events.filter(e => e.event_type === 'support_bounce');

    const traces = [];

    if (resistanceEvents.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: resistanceEvents.map(e => e.event_timestamp),
        y: resistanceEvents.map(e => e.resistance_level),
        name: 'Resistance Events',
        marker: {
          color: '#ff9800',
          size: 8,
          symbol: 'triangle-down',
          line: {
            color: '#fff',
            width: 1,
          },
        },
        hovertemplate: 
          '<b>Resistance Event</b><br>' +
          'Time: %{x}<br>' +
          'Level: %{y:.5f}<br>' +
          'Rebound: %{customdata}%<br>' +
          '<extra></extra>',
        customdata: resistanceEvents.map(e => (e.rebound_percentage * 100).toFixed(2)),
        ids: resistanceEvents.map(e => e.id),
      });
    }

    if (supportEvents.length > 0) {
      traces.push({
        type: 'scatter',
        mode: 'markers',
        x: supportEvents.map(e => e.event_timestamp),
        y: supportEvents.map(e => e.resistance_level),
        name: 'Support Events',
        marker: {
          color: '#2196f3',
          size: 8,
          symbol: 'triangle-up',
          line: {
            color: '#fff',
            width: 1,
          },
        },
        hovertemplate: 
          '<b>Support Event</b><br>' +
          'Time: %{x}<br>' +
          'Level: %{y:.5f}<br>' +
          'Rebound: %{customdata}%<br>' +
          '<extra></extra>',
        customdata: supportEvents.map(e => (e.rebound_percentage * 100).toFixed(2)),
        ids: supportEvents.map(e => e.id),
      });
    }

    return traces;
  }, [events]);

  // Highlight selected event
  const selectedEventTrace = useMemo(() => {
    if (!selectedEvent) return null;

    return {
      type: 'scatter',
      mode: 'markers',
      x: [selectedEvent.event_timestamp],
      y: [selectedEvent.resistance_level],
      name: 'Selected Event',
      marker: {
        color: '#f44336',
        size: 15,
        symbol: 'star',
        line: {
          color: '#fff',
          width: 2,
        },
      },
      showlegend: false,
      hovertemplate: 
        '<b>Selected Event</b><br>' +
        'Time: %{x}<br>' +
        'Level: %{y:.5f}<br>' +
        '<extra></extra>',
    };
  }, [selectedEvent]);

  // Volume trace
  const volumeTrace = useMemo(() => {
    if (!showVolume || !candles || candles.length === 0) return null;

    return {
      type: 'bar',
      x: candles.map(c => c.timestamp),
      y: candles.map(c => c.volume || 0),
      name: 'Volume',
      yaxis: 'y2',
      marker: {
        color: candles.map(c => c.close >= c.open ? '#26a69a' : '#ef5350'),
        opacity: 0.5,
      },
      hovertemplate: 
        'Volume: %{y:,.0f}<br>' +
        '<extra></extra>',
    };
  }, [candles, showVolume]);

  // Combine all traces
  const data = useMemo(() => {
    const traces = [];
    
    if (candlestickTrace) traces.push(candlestickTrace);
    traces.push(...resistanceLines);
    if (eventMarkers) traces.push(...eventMarkers);
    if (selectedEventTrace) traces.push(selectedEventTrace);
    if (volumeTrace) traces.push(volumeTrace);
    
    return traces;
  }, [candlestickTrace, resistanceLines, eventMarkers, selectedEventTrace, volumeTrace]);

  // Chart layout
  const layout = useMemo(() => {
    const baseLayout = {
      title: {
        text: `${instrument} - ${timeframe}`,
        font: { size: 16 },
      },
      height: height,
      margin: { t: 40, b: 40, l: 60, r: 60 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: '#ffffff',
      xaxis: {
        rangeslider: { visible: false },
        type: 'date',
        gridcolor: '#e0e0e0',
        showgrid: true,
      },
      yaxis: {
        title: 'Price',
        side: 'right',
        gridcolor: '#e0e0e0',
        showgrid: true,
        domain: showVolume ? [0.3, 1] : [0, 1],
      },
      hovermode: 'x unified',
      dragmode: 'zoom',
      showlegend: true,
      legend: {
        orientation: 'h',
        yanchor: 'bottom',
        y: 1.02,
        xanchor: 'right',
        x: 1,
      },
    };

    if (showVolume) {
      return {
        ...baseLayout,
        yaxis2: {
          title: 'Volume',
          side: 'right',
          overlaying: 'y',
          domain: [0, 0.25],
          gridcolor: '#e0e0e0',
          showgrid: false,
        },
      };
    }

    return baseLayout;
  }, [instrument, timeframe, height, showVolume]);

  // Chart config
  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: `${instrument}_${timeframe}_${format(new Date(), 'yyyy-MM-dd')}`,
      height: 800,
      width: 1200,
      scale: 1,
    },
  };

  // Handle click on plot
  const handlePlotClick = (data: any) => {
    if (onEventClick && data.points && data.points.length > 0) {
      const point = data.points[0];
      if (point.data.ids) {
        const eventId = point.data.ids[point.pointIndex];
        const event = events.find(e => e.id === eventId);
        if (event) {
          onEventClick(event);
        }
      }
    }
  };

  if (!candles || candles.length === 0) {
    return (
      <div className={`flex items-center justify-center bg-white dark:bg-gray-800 rounded-lg ${className}`} style={{ height }}>
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500 dark:text-gray-400">No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm ${className}`}>
      <Plot
        data={data}
        layout={layout}
        config={config}
        onClickannotation={handlePlotClick}
        onClick={handlePlotClick}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler
      />
    </div>
  );
};