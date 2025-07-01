"""
Chart components for dashboard
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Optional, Union
import numpy as np


def render_time_series_chart(
        df: pd.DataFrame,
        y_columns: Union[str, List[str]],
        title: str,
        y_label: str = "Value",
        height: int = 400,
        show_legend: bool = True,
        line_colors: Optional[List[str]] = None
) -> None:
    """
    Render time series line chart

    Args:
        df: DataFrame with datetime index
        y_columns: Column(s) to plot
        title: Chart title
        y_label: Y-axis label
        height: Chart height
        show_legend: Whether to show legend
        line_colors: Custom line colors
    """
    if df.empty:
        st.warning("No data available for the selected period")
        return

    # Ensure y_columns is a list
    if isinstance(y_columns, str):
        y_columns = [y_columns]

    # Create figure
    fig = go.Figure()

    # Default colors if not provided
    if not line_colors:
        line_colors = px.colors.qualitative.Set2

    # Add traces
    for i, col in enumerate(y_columns):
        if col in df.columns:
            color = line_colors[i % len(line_colors)]
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=col,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{col}</b><br>Date: %{{x}}<br>Value: %{{y:,.2f}}<extra></extra>'
            ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        height=height,
        showlegend=show_legend,
        hovermode='x unified',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    # Update axes
    fig.update_xaxis(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        color_column: Optional[str] = None,
        orientation: str = "v",
        height: int = 400,
        show_values: bool = True
) -> None:
    """
    Render bar chart

    Args:
        df: DataFrame
        x_column: X-axis column
        y_column: Y-axis column
        title: Chart title
        color_column: Column for color grouping
        orientation: 'v' for vertical, 'h' for horizontal
        height: Chart height
        show_values: Whether to show values on bars
    """
    if df.empty:
        st.warning("No data available")
        return

    # Create figure
    if color_column and color_column in df.columns:
        fig = px.bar(
            df,
            x=x_column if orientation == "v" else y_column,
            y=y_column if orientation == "v" else x_column,
            color=color_column,
            title=title,
            orientation=orientation,
            height=height
        )
    else:
        fig = px.bar(
            df,
            x=x_column if orientation == "v" else y_column,
            y=y_column if orientation == "v" else x_column,
            title=title,
            orientation=orientation,
            height=height
        )

    # Update layout
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=bool(color_column)
    )

    # Show values on bars
    if show_values:
        fig.update_traces(
            texttemplate='%{y:,.0f}' if orientation == "v" else '%{x:,.0f}',
            textposition="outside"
        )

    st.plotly_chart(fig, use_container_width=True)


def render_stacked_area_chart(
        df: pd.DataFrame,
        columns: List[str],
        title: str,
        y_label: str = "Value",
        height: int = 400,
        percentage: bool = False
) -> None:
    """
    Render stacked area chart

    Args:
        df: DataFrame with datetime index
        columns: Columns to stack
        title: Chart title
        y_label: Y-axis label
        height: Chart height
        percentage: Whether to show as percentage
    """
    if df.empty:
        st.warning("No data available")
        return

    # Filter columns that exist
    valid_columns = [col for col in columns if col in df.columns]
    if not valid_columns:
        st.warning("No valid columns found")
        return

    # Create figure
    fig = go.Figure()

    # Calculate percentages if needed
    if percentage:
        df_pct = df[valid_columns].div(df[valid_columns].sum(axis=1), axis=0) * 100
        df_plot = df_pct
        y_label = f"{y_label} (%)"
    else:
        df_plot = df[valid_columns]

    # Add traces
    for col in valid_columns:
        fig.add_trace(go.Scatter(
            x=df_plot.index,
            y=df_plot[col],
            mode='lines',
            name=col,
            stackgroup='one',
            hovertemplate=f'<b>{col}</b><br>Date: %{{x}}<br>Value: %{{y:,.2f}}<extra></extra>'
        ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        height=height,
        hovermode='x unified',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_comparison_chart(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        y1_column: str,
        y2_column: str,
        title: str,
        y1_label: str = "Series 1",
        y2_label: str = "Series 2",
        height: int = 400
) -> None:
    """
    Render dual-axis comparison chart

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        y1_column: Column from df1
        y2_column: Column from df2
        title: Chart title
        y1_label: Label for first y-axis
        y2_label: Label for second y-axis
        height: Chart height
    """
    if df1.empty or df2.empty:
        st.warning("Insufficient data for comparison")
        return

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add first trace
    fig.add_trace(
        go.Scatter(
            x=df1.index,
            y=df1[y1_column],
            name=y1_label,
            line=dict(color='blue', width=2)
        ),
        secondary_y=False,
    )

    # Add second trace
    fig.add_trace(
        go.Scatter(
            x=df2.index,
            y=df2[y2_column],
            name=y2_label,
            line=dict(color='red', width=2)
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=y1_label, secondary_y=False)
    fig.update_yaxes(title_text=y2_label, secondary_y=True)

    fig.update_layout(
        title=title,
        height=height,
        hovermode='x unified',
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_heatmap(
        df: pd.DataFrame,
        title: str,
        color_scale: str = "RdBu_r",
        height: int = 400,
        show_values: bool = True
) -> None:
    """
    Render heatmap

    Args:
        df: DataFrame (typically with hour as index, date as columns)
        title: Chart title
        color_scale: Plotly color scale
        height: Chart height
        show_values: Whether to show values in cells
    """
    if df.empty:
        st.warning("No data available")
        return

    # Create figure
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=color_scale,
        hoverongaps=False,
        showscale=True,
        text=df.values if show_values else None,
        texttemplate="%{text:.1f}" if show_values else None,
        textfont={"size": 10}
    ))

    # Update layout
    fig.update_layout(
        title=title,
        height=height,
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(title="Date"),
        yaxis=dict(title="Hour")
    )

    st.plotly_chart(fig, use_container_width=True)


def render_pie_chart(
        df: pd.DataFrame,
        values_column: str,
        names_column: str,
        title: str,
        height: int = 400,
        show_legend: bool = True
) -> None:
    """
    Render pie chart

    Args:
        df: DataFrame
        values_column: Column with values
        names_column: Column with names/labels
        title: Chart title
        height: Chart height
        show_legend: Whether to show legend
    """
    if df.empty:
        st.warning("No data available")
        return

    # Create figure
    fig = px.pie(
        df,
        values=values_column,
        names=names_column,
        title=title,
        height=height
    )

    # Update layout
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=show_legend
    )

    # Update traces
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percent: %{percent}<extra></extra>'
    )

    st.plotly_chart(fig, use_container_width=True)


def render_box_plot(
        df: pd.DataFrame,
        y_column: str,
        group_column: Optional[str],
        title: str,
        y_label: str = "Value",
        height: int = 400
) -> None:
    """
    Render box plot for distribution analysis

    Args:
        df: DataFrame
        y_column: Column with values
        group_column: Optional grouping column
        title: Chart title
        y_label: Y-axis label
        height: Chart height
    """
    if df.empty:
        st.warning("No data available")
        return

    # Create figure
    if group_column and group_column in df.columns:
        fig = px.box(
            df,
            x=group_column,
            y=y_column,
            title=title,
            height=height
        )
    else:
        fig = px.box(
            df,
            y=y_column,
            title=title,
            height=height
        )

    # Update layout
    fig.update_layout(
        yaxis_title=y_label,
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)