"""
Chart components for stock visualization using Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional


def create_candlestick_chart(
    historical_data: Dict,
    symbol: str,
    prediction_direction: Optional[str] = None,
    prediction_confidence: Optional[float] = None
) -> go.Figure:
    """
    Create an interactive candlestick chart with volume.

    Args:
        historical_data: Dictionary with dates as keys, OHLCV data as values
        symbol: Stock symbol for title
        prediction_direction: Optional 'UP' or 'DOWN' for annotation
        prediction_confidence: Optional confidence score

    Returns:
        Plotly figure object
    """
    if not historical_data:
        return None

    # Convert dict to DataFrame
    df = pd.DataFrame.from_dict(historical_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))

    # Update layout
    title_text = f"{symbol} - Last 60 Days"
    if prediction_direction and prediction_confidence:
        emoji = "📈" if prediction_direction == "UP" else "📉"
        title_text += f" | Prediction: {emoji} {prediction_direction} ({prediction_confidence:.1%})"

    fig.update_layout(
        title=title_text,
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_white",
        height=400,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=False
    )

    # Format y-axis for Indian Rupees
    fig.update_yaxes(tickprefix="₹")

    return fig


def create_line_chart_with_volume(
    historical_data: Dict,
    symbol: str,
    prediction_direction: Optional[str] = None,
    prediction_confidence: Optional[float] = None
) -> go.Figure:
    """
    Create a line chart with volume bars below.

    Args:
        historical_data: Dictionary with dates as keys, OHLCV data as values
        symbol: Stock symbol for title
        prediction_direction: Optional 'UP' or 'DOWN' for annotation
        prediction_confidence: Optional confidence score

    Returns:
        Plotly figure object with subplots
    """
    if not historical_data:
        return None

    # Convert dict to DataFrame
    df = pd.DataFrame.from_dict(historical_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Create subplots
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price', 'Volume'),
        row_heights=[0.7, 0.3]
    )

    # Add close price line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            name='Close Price',
            line=dict(color='#2962ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(41, 98, 255, 0.1)'
        ),
        row=1, col=1
    )

    # Add volume bars
    colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350'
              for i in range(len(df))]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )

    # Update layout
    title_text = f"{symbol} - Last 60 Days"
    if prediction_direction and prediction_confidence:
        emoji = "📈" if prediction_direction == "UP" else "📉"
        title_text += f" | Prediction: {emoji} {prediction_direction} ({prediction_confidence:.1%})"

    fig.update_layout(
        title_text=title_text,
        template="plotly_white",
        height=500,
        hovermode='x unified',
        showlegend=False
    )

    # Format axes
    fig.update_yaxes(title_text="Price (₹)", tickprefix="₹", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig


def create_simple_line_chart(
    historical_data: Dict,
    symbol: str,
    show_sma: bool = False
) -> go.Figure:
    """
    Create a simple close price line chart.

    Args:
        historical_data: Dictionary with dates as keys, OHLCV data as values
        symbol: Stock symbol for title
        show_sma: Whether to show 20-day SMA

    Returns:
        Plotly figure object
    """
    if not historical_data:
        return None

    # Convert dict to DataFrame
    df = pd.DataFrame.from_dict(historical_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    fig = go.Figure()

    # Add close price
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        name='Close Price',
        line=dict(color='#2962ff', width=2),
        mode='lines'
    ))

    # Add SMA if requested
    if show_sma and len(df) >= 20:
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            name='20-Day SMA',
            line=dict(color='#ff6d00', width=1, dash='dash'),
            mode='lines'
        ))

    fig.update_layout(
        title=f"{symbol} - Close Price Trend",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        template="plotly_white",
        height=350,
        hovermode='x unified'
    )

    fig.update_yaxes(tickprefix="₹")

    return fig
